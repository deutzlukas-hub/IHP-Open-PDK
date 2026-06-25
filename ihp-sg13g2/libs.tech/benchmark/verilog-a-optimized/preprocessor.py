#!/usr/bin/env python3
"""
Verilog-A Constant Propagation Preprocessor

Propagates constants through Verilog-A dump files to simplify expressions.
Performs iterative constant propagation starting from localparams.
"""

import re
import math
from pathlib import Path
from typing import List, Mapping
from enum import Flag, auto
from collections import Counter, defaultdict
from dataclasses import dataclass

@dataclass(frozen=True)
class BlockRange:
    block_id: int
    name: str | None
    start_line: int
    end_line: int
    depth: int = 0

@dataclass(frozen=True)
class VarDecl:
    name: str
    var_type: str
    line_num: int

@dataclass(frozen=True)
class Assignment():
    line_idx: int
    lhs: str
    rhs: str
    in_control: bool

class Transform(Flag):
    NONE = 0
    PRUNE_LITERAL_IFS = auto()
    RENAME_LOCAL_VARS = auto()
    REMOVE_STALE_DECLARATIONS = auto()

class PostPreproccesor:
    """Parse Verilog-A dump files and extract constants and assignments."""

    MODULE_HEAD_RE = re.compile(r'module\s+([A-Za-z_]\w*)\s*\(([^)]*)\)')

    def __init__(self, file: Path):

        content = file.read_text()
        self.lines = content.splitlines(keepends=True)
        self.modules = {}

    def apply_transforms(self, transforms: Transform):

        for module in self.modules.values():
            module.apply_transform(transforms)

        # Rebuild self.lines from modified modules
        self._rebuild_lines_from_transformed_modules()

        return "".join(self.lines)

    def optimize(self,
        max_iters: int = 20,
        already_prepared: bool = False
    ) -> str:

        for module in self.modules.values():
            module.optimize(max_iters, already_prepared)

        # Rebuild self.lines from modified modules
        self._rebuild_lines_from_transformed_modules()

        return "".join(self.lines)

    def _rebuild_lines_from_transformed_modules(self):

        # sort modules by start line from bottom to top
        modules = sorted(
            self.modules.values(),
            key=lambda m: m.start_line,
            reverse=True)

        # iterate from bottom to top modules
        for module in modules:
            self.lines[module.start_line:module.end_line+1] = module.content


    def parse(self):

        current_module = None

        for line_num, line in enumerate(self.lines):

            stripped = line.strip()

            if stripped.startswith('module'):
                match = self.MODULE_HEAD_RE.search(line)
                assert match is not None, f"Invalid module header line: {line}"

                module_name = match.group(1)
                terminals =  [p.strip() for p  in match.group(2).split(',')]

                current_module = Module(module_name, terminals)
                current_module.start_line = line_num
                self.modules[module_name] = current_module

            if stripped.startswith('endmodule'):
                current_module.end_line = line_num
                current_module.content.append(line)
                current_module = None
                continue

            if current_module is not None:
                current_module.content.append(line)

        # for module in self.modules.values():
            # module.find_analog_blocks()
            # mdoesn not.odule.parse_params_and_vars()

class Module():

    #---------------------------------------------------------------------------
    # Regular Expressions

    IDENTIFIER = r'[A-Za-z_][A-Za-z0-9_$]*'
    IDENTIFIER_RE = re.compile(IDENTIFIER)

    #---------------------------------------------------------------------------
    # Blocks

    BLOCK_TOKEN_RE = re.compile(
        rf'\bbegin\b(?:\s*:\s*(?P<name>{IDENTIFIER}))?|\bend\b'
    )

    #---------------------------------------------------------------------------
    # Parameters

    PARAM_RE = re.compile(
        r'^\s*parameter\s+'
        r'(?P<type>real|integer)\s+'
        r'(?P<name>\w+)\s*=\s*'
        r'(?P<default_value>.*?)'
        r'\s*;\s*$'
    )

    LOCALPARAM_RE = re.compile(
        r'^\s*localparam\s+'
        r'(?P<param_type>real|integer)\s+'
        r'(?P<name>__\w+)\s*=\s*'
        r'(?P<expr>.*?)'
        r'\s*;\s*$'
    )

    # multiple variable declarations per line
    VARDECL_RE = re.compile(
        r'^\s*(?P<var_type>real|integer)\s+'
        r'(?P<names>.*?)'
        r'\s*;\s*$'
    )

    # only one outvar declaration per line
    OUTVAR_DECL_RE = re.compile(
        r'(?P<type>real|integer)\s+'
        r'(?P<name>[A-Za-z_]\w*)'
        r'\s*;\s*$'
    )

    #---------------------------------------------------------------------------
    # Attributes

    ATTRIBUTE_RE = re.compile(
        r'^\s*\(\*\s*'
        r'(?P<attrs>.*?)'
        r'\s*\*\)\s*$'
    )

    ATTRIBUTE_PAIR_RE = re.compile(
        r'(?P<name>\w+)\s*=\s*'
        r'"(?P<value>[^"]*)"'
    )


    #---------------------------------------------------------------------------
    # Assignments


    ASSIGNMENT_RE = re.compile(
        rf'^\s*'
        rf'(?P<lhs>{IDENTIFIER})\s*=\s*'
        rf'(?P<rhs>.*?)'
        rf'\s*;\s*'
        rf'(?://.*)?$'
    )

    NUM_LITERAL = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'

    NUM_LITERAL_RE = re.compile(rf'^\s*{NUM_LITERAL}\s*$')

    DECLARATION_RE = re.compile(r'^(\s*)(integer|real)\s+(.+?)\s*;\s*$')

    #---------------------------------------------------------------------------
    # Conditionals

    CONTROL_ANALOG_BEGIN_RE = re.compile(
        r'^\s*analog\s+begin\b'
    )

    CONTROL_PLAIN_BEGIN_RE = re.compile(
        r'^\s*begin\b(?:\s*:\s*[A-Za-z_]\w*)?\s*$'
    )

    CONTROL_IF_BEGIN_RE = re.compile(
        r'^\s*if\s*\(.*\)\s*begin\b'
    )

    CONTROL_ELSE_BEGIN_RE = re.compile(
        r'^\s*else\s+begin\b'
    )

    CONTROL_WHILE_BEGIN_RE = re.compile(
        r'^\s*while\s*\(.*\)\s*begin\b'
    )

    CONTROL_END_RE = re.compile(
        r'^\s*end\b'
    )

    #---------------------------------------------------------------------------
    # pruning literal if/else blocks

    IF_RE = re.compile(
        r'^(?P<prefix>\s*if\s*\()'
        r'(?P<cond>.*)'
        r'(?P<suffix>\)\s*begin\s*)$'
    )

    IF_CONST_RE = re.compile(
        r'^\s*if\s*\(\s*(?P<value>[01])\s*\)\s*begin\s*$'
    )
    ELSE_BEGIN_RE = re.compile(
        r'^\s*else\s*begin\s*$'
    )

    BEGIN_RE = re.compile(
        r'\bbegin\b'
    )
    END_RE = re.compile(
        r'\bend\b'
    )

    NAMED_BEGIN_RE = re.compile(
        r'^\s*begin\s*:\s*(?P<name>[A-Za-z_]\w*)\s*$'
    )

    def __init__(self,
        name: str,
        terminals: List[str],
        ):

        self.name = name
        self.terminals = terminals

        self.content = []
        # parmeter and variable container
        self.var_decls: list[VarDecl] = []

        self.localparams: dict[str, tuple[str, str, int]] = {}
        self.instance_params: set[str] = set()
        self.out_vars: dict[str, tuple[str, int]] = {}
        self.vars: dict[str, tuple[str, int]] = {}

        self.constants: dict[str, str] = {}

        # track position in original file
        self.start_line = None
        self.end_line = None

        # so we can not rename twice
        self.renamed_local_vars = False
    #------------------------------------------------------------------------------
    # Public Class API

    def apply_transform(self, transforms: Transform | list[Transform]):
        """Apply selected non-iterative transforms to this module."""

        if isinstance(transforms, Transform):
            transforms = [transforms]

        for transform in transforms:

            if transform == Transform.PRUNE_LITERAL_IFS:
                self._prune_literal_ifs()

            elif transform == Transform.RENAME_LOCAL_VARS:
                self._rename_local_vars()

            elif transform == Transform.REMOVE_STALE_DECLARATIONS:
                self._remove_stale_declarations()

            else:
                assert False, f"Unknown transform: {transform}"

    def prepare_for_optimization(self) -> None:
        # One-time structural prep
        self._prune_literal_ifs()
        self._rename_local_vars()
        self._remove_stale_declarations()

    def optimize(self,
        max_iters: int = 20,
        already_prepared: bool = False,
    ) -> None:

        if not already_prepared:
            self.prepare_for_optimization()

        self._parse_declarations()
        self._collect_constant_localparams()

        # optimization loop
        for i in range(max_iters):
            print("optimize: ", i, " ", end="")

            old_content = self.content.copy()

            # Ordered propagation of constants
            self._propagate_constants_ordered()
            # Propagation may have created if (0) / if (1)
            self._prune_literal_ifs()

            if self.content == old_content:
                print("fixed point")
                break
        else:
            raise RuntimeError("constant propagation did not reach fixed point")

        # Final cosmetic clean-up
        self._remove_stale_declarations(max_iters)

    #===========================================================================
    # Block discovery and local variable renaming
    #===========================================================================

    def _find_analog_blocks(self) -> list[BlockRange]:
        """
        Find named begin/end blocks inside the analog block.
        """
        blocks: list[BlockRange] = []

        in_analog = False
        depth = 0
        next_block_id = 1

        block_stack: list[dict] = []

        for line_num, line in enumerate(self.content):
            stripped = line.strip()

            # Enter analog block
            if stripped.startswith('analog begin'):
                in_analog = True
                depth = 1
                continue

            if not in_analog:
                continue

            # Find all block boundary tokens on this line
            #   begin
            #   begin: name
            #   end
            for match in self.BLOCK_TOKEN_RE.finditer(stripped):

                token = match.group(0)
                if token.startswith("begin"):
                    depth += 1
                    block_name = match.group("name")
                    # Entering new block
                    if block_name is not None:
                        block_stack.append(
                            {
                                "block_id": next_block_id,
                                "name": block_name,
                                "start_line": line_num,
                                "depth": depth,
                            }
                        )
                        next_block_id +=1

                elif token == "end":
                    if block_stack and block_stack[-1]["depth"] == depth:
                        block = block_stack.pop()
                        blocks.append(
                            BlockRange(
                                block_id = block["block_id"],
                                name = block["name"],
                                start_line = block["start_line"],
                                end_line = line_num,
                                depth = block["depth"],
                            )
                        )

                    depth -= 1

                # Leaving analog block
                if depth == 0:
                    in_analog = False
                    break

            assert depth >= 0, (
                f"Unbalanced begin/end near line {line_num}: {line.rstrip()!r}"
            )

        assert not in_analog, "Unclosed analog block"
        assert not block_stack, (
            f"Unclosed named block inside analog block, "
            f"{block_stack}"
        )

        return sorted(blocks, key=lambda block: block.depth, reverse=True)

    def _innermost_block_for_line(self,
            blocks: list[BlockRange],
            line_num: int,
    ) -> BlockRange:
        """Find the innermost block that contains the given line number."""

        containing = [
            block
            for block in blocks
            if block.start_line < line_num < block.end_line
        ]

        assert containing, "No block contains var declaration. This is a bug."

        return max(containing, key=lambda block: block.depth)

    def _rename_local_vars(self) -> None:
        """
        Rename local scope variables in the analog block to unique names to
        flat constant propagation.
        """

        if self.renamed_local_vars:
            return

        blocks = self._find_analog_blocks()
        # Rename inner blocks before outer blocks.

        var_decls_by_block: dict[int, list[VarDecl]] = defaultdict(list)

        block_var_decls = self._collect_block_var_decls(blocks)

        for var_decl in block_var_decls:

            block = self._innermost_block_for_line(blocks, var_decl.line_num)
            var_decls_by_block[block.block_id].append(var_decl)

        for block in blocks:

            var_decls_in_block = var_decls_by_block[block.block_id]

            if not var_decls_in_block:
                continue

            names = [var_decl.name for var_decl in var_decls_in_block]

            assert len(names) == len(set(names)),(
                f"Duplicate variable declaration in block {block.name!r}: {names}"
            )

            renames = {
                name: f"{name}__b{block.block_id}"
                for name in names
            }

            for line_num in range(block.start_line, block.end_line + 1):
                line = self.content[line_num]

                code, sep, comment = line.partition("//")

                def replace_identifier(match: re.Match) -> str:
                    """Return renamed identifier"""
                    identifier = match.group(0)
                    return renames.get(identifier, identifier)

                new_code = self.IDENTIFIER_RE.sub(replace_identifier, code)
                self.content[line_num] = new_code + sep + comment

            self.renamed_local_vars = True

    def _collect_block_var_decls(self, blocks) -> list[VarDecl]:

        block_var_decls: list[VarDecl] = []

        in_analog = False
        depth = 0

        for line_num, line in enumerate(self.content):
            stripped = line.strip()

            if stripped.startswith("analog begin"):
                in_analog = True
                depth = 1
                continue

            if not in_analog:
                continue

            for match in self.BLOCK_TOKEN_RE.finditer(stripped):
                token = match.group(0)

                if token.startswith("begin"):
                    depth += 1
                elif token == "end":
                    depth -= 1

            assert depth >= 0, (
                f"Unbalanced begin/end near line {line_num}: {line.rstrip()!r}"
            )

            if depth == 0:
                in_analog = False
                continue

            if depth > 1:
                if not stripped.startswith(("real", "integer")):
                    continue

                # this asserts if line is not in local block
                self._innermost_block_for_line(blocks, line_num)

                var_type, var_names = self._parse_var_decl_line(stripped, line_num)

                for var_name in var_names:
                    block_var_decls.append(
                        VarDecl(
                            var_name,
                            var_type,
                            line_num,
                        )
                    )

        assert not in_analog, "Unclosed analog block"
        return block_var_decls

    #===========================================================================
    # Declaration parsing
    #===========================================================================

    def _parse_declarations(self):
        """
        Parse parameter and variable declarations.
        """
        self.instance_params.clear()
        self.localparams.clear()
        self.out_vars.clear()
        self.vars.clear()

        lines = self.content
        next_has_desc = False
        in_analog = False

        for line_num, line in enumerate(lines):

            stripped = line.strip()

            if stripped.startswith('analog begin'):
                in_analog = True
                continue

            if stripped.startswith('(*'):
                # Attribute line for next declaration
                attrs = self._parse_attribute_line(line, line_num)
                next_has_desc = "desc" in attrs

            elif stripped.startswith('parameter'):
                # must be in analog
                assert not in_analog, (
                    f"parameter declaration inside analog block {line_num}: "
                    f"{line.rstrip()!r}"
                )
                # Instance param with default value, unknown at compile time
                name, _, _ = self._parse_parameter_line(stripped, line_num)
                assert name not in self.localparams, (
                    f"parameter {name} declared twice"
                    f"{line}"
                )

                # Unkown at compile time: only save name
                self.instance_params.add(name)
                next_has_desc = False

            elif stripped.startswith('localparam'):
                # must be in analog
                assert not in_analog, (
                    f"localparam declaration inside analog block: "                    
                    f"{line.rstrip()!r}"
                )

                # localparam declaration with initializer
                name, param_type, expr = self._parse_localparam_line(stripped, line_num)

                assert name not in self.localparams, (
                    f"localparam {name} declared twice"
                    f"{line}"
                )

                self.localparams[name] = (param_type, expr, line_num)
                next_has_desc = False

            elif stripped.startswith('integer') or stripped.startswith('real'):
                if not next_has_desc:
                    # variable declarations
                    var_type, var_names = self._parse_var_decl_line(stripped, line_num)
                    for var_name in var_names:
                        assert var_name not in self.vars, (
                            f"variable {var_name} declared twice"
                            f"{line}"
                        )
                        self.vars[var_name] = (var_type, line_num)
                else:
                    # outvar declaration
                    assert not in_analog, (
                        f"outvar declaration inside analog block {line_num}: "
                        f"{line.rstrip()!r}"
                    )
                    outvar_type, outvar_name = self._parse_outvar_decl_line(stripped, line_num)
                    self.out_vars[outvar_name] = (outvar_type, line_num)

                next_has_desc = False

            else:
                assert not next_has_desc, (
                    f"desc attribute was not followed by a declaration at line {line_num}: "
                    f"{line!r}"
                )

    def _parse_parameter_line(self, line: str, line_num: int):

        match = self.PARAM_RE.match(line)

        assert match is not None, f"Invalid instance parameter assignment line: {line}"

        return (
            match.group("name"),
            match.group("type"),
            match.group("default_value").strip(),
        )

    def _parse_localparam_line(self, line, linenum):

        match = self.LOCALPARAM_RE.match(line)
        assert match is not None, f"Invalid localparam assignment line: {line}"

        return (
            match.group("name"),
            match.group("param_type"),
            match.group("expr").strip(),
        )

    def _parse_var_decl_line(self, line: str, line_num: int):
        """Parse variable declaration line like 'real var1, var2, var3;'"""

        match = self.VARDECL_RE.match(line)

        assert match is not None, f"Invalid variable declaration line: {line}"

        var_type = match.group("var_type")
        names_str = match.group("names")

        # Split comma-separated variable names and strip whitespace
        var_names = [name.strip() for name in names_str.split(',')]

        return var_type, var_names

    def _parse_attribute_line(self, line: str, line_num: int):
        """Parse attribute line like '(* attribute *)"""

        match = self.ATTRIBUTE_RE.match(line)
        assert match is not None, (
            f"Expected attribute line at {line_num}, got: {line!r}"
        )

        attr_text = match.group("attrs").strip()

        return {
            name: value
            for name, value in self.ATTRIBUTE_PAIR_RE.findall(attr_text)
        }

    def _parse_outvar_decl_line(self, line: str, line_num: int):
        """Parse outvar line like 'outvar = var1 + var2;'"""

        match = self.OUTVAR_DECL_RE.match(line)
        assert match is not None, (
            f"Expected outvar assignment at {line_num}, got: {line!r}"
        )

        outvar_type = match.group("type")
        outvar_name = match.group("name")

        return outvar_type, outvar_name

    def _declared_type(self, name: str) -> str:
        if name in self.vars:
            return self.vars[name][0]

        if name in self.out_vars:
            return self.out_vars[name][0]

        if name in self.localparams:
            return self.localparams[name][0]

        raise KeyError(f"Unknown declared identifier {name!r}")

    def _has_attribute_before(self, line_num: int) -> bool:
        if line_num == 0:
            return False

        return self.ATTRIBUTE_RE.match(self.content[line_num - 1]) is not None

    #===========================================================================
    # Collect compile-time constants
    #===========================================================================

    def _collect_constant_localparams(self) -> None:
        """
        Collect all localparams that are constants.
        """
        self.constants.clear()

        for name, (param_type, expr, line_num) in self.localparams.items():

            expr_sub = ExpressionEvaluator.substitute_constants(
                expr=expr,
                constants=self.constants,
            )

            value = ExpressionEvaluator.try_eval_typed(
                expr=expr_sub,
                value_type=param_type,
            )

            if value is None:
                # Legal if it depends on an instance parameter that we do not know
                # at compile time. Do not add it to self.constants.
                continue

            self.constants[name] = value

        return

    #===========================================================================
    # Ordered constant propagation
    #===========================================================================

    def _propagate_constants_ordered(self):

        new_content = self.content.copy()
        constants = self.constants.copy()

        control_stack: list[bool] = []

        try:
            for line_idx, line in enumerate(self.content):

                stripped_after_end = self._pop_control_stack(line, control_stack)

                in_control = any(control_stack)

                if match := self.ASSIGNMENT_RE.match(line):
                    new_content[line_idx] = self._fold_assignment(
                        line, match, constants, in_control
                    )
                elif match := self.IF_RE.match(line):
                    new_content[line_idx] = self._fold_if_cond(
                        line, match, constants,
                    )
                # TODO:
                # elif match := self.CONTRIBUTION_RE.match(line):
                #     pass

                self._push_control_stack(stripped_after_end, control_stack, in_control)

        except Exception as exc:
            print("Ordered constant propagation failed")
            print(f"module: {self.name}")
            print(self._debug_context(line_idx))
            print(f"control_stack: {control_stack}")
            raise

        assert not control_stack, "Unclosed begin/end block after ordered propagation"

        self.content = new_content

        return

    def _debug_context(self, line_idx: int, radius: int = 8) -> str:
        start = max(0, line_idx - radius)
        end = min(len(self.content), line_idx + radius + 1)

        out = []
        for idx in range(start, end):
            marker = ">>" if idx == line_idx else "  "
            out.append(f"{marker} {idx + 1:6d}: {self.content[idx].rstrip()}")
        return "\n".join(out)

    def _fold_assignment(self,
        line: str,
        match: re.Match[str],
        constants: dict[str, str],
        in_control: bool = False,
    ) -> str:

        rhs = match.group("rhs")
        lhs = match.group("lhs")

        rhs_sub = ExpressionEvaluator.substitute_constants(
            expr=rhs,
            constants=constants
        )

        value_type = self._declared_type(lhs)

        folded_rhs = ExpressionEvaluator.try_eval_typed(
            expr=rhs_sub,
            value_type=value_type,
        )

        if folded_rhs is not None:
            new_rhs = folded_rhs
        else:
            new_rhs = rhs_sub

        if in_control:
            # assignent may not execute, so lhs is not reliably constant afterwards
            constants.pop(lhs, None)

        elif folded_rhs is not None:
            # from his point onward, lhs has a known constant value
            constants[lhs] = folded_rhs

        else:
            # lhs was assigned a runtime-dependent expression.
            constants.pop(lhs, None)

        if new_rhs == rhs:
            return line

        return line[:match.start("rhs")] + new_rhs + line[match.end("rhs"):]

    def _fold_if_cond(self,
        line: str,
        match: re.Match[str],
        constants: dict[str, str],
    ) ->  str:

        cond = match.group("cond").strip()

        cond_sub = ExpressionEvaluator.substitute_constants(
            expr=cond,
            constants=constants,
        )

        folded_cond = ExpressionEvaluator.try_eval_cond(expr=cond_sub)

        if folded_cond is not None:
            new_cond = folded_cond
        else:
            new_cond = cond_sub

        if new_cond == cond:
            return line

        return (
                line[:match.start("cond")]
                + new_cond
                + line[match.end("cond"):]
        )

    def _pop_control_stack(self,
        line: str,
        control_stack: list[bool],
    ) -> str:

        stripped = line.strip()

        # Consume leading end tokens.
        while True:
            match = self.CONTROL_END_RE.match(stripped)
            if match is None:
                break

            assert control_stack, "Unexpected end without matching begin"

            control_stack.pop()
            stripped = stripped[match.end():].strip()

        return stripped

    def _push_control_stack(self,
        stripped_after_end: str,
        control_stack: list[bool],
        in_control: bool,
    ) -> None:
        if self.CONTROL_ANALOG_BEGIN_RE.match(stripped_after_end) is not None:
            control_stack.append(False)
            return

        if self.CONTROL_IF_BEGIN_RE.match(stripped_after_end) is not None:
            control_stack.append(True)
            return

        if self.CONTROL_ELSE_BEGIN_RE.match(stripped_after_end) is not None:
            control_stack.append(True)
            return

        if self.CONTROL_PLAIN_BEGIN_RE.match(stripped_after_end) is not None:
            control_stack.append(in_control)
            return

        if self.CONTROL_WHILE_BEGIN_RE.match(stripped_after_end) is not None:
            control_stack.append(True)
            return

    #===========================================================================
    # Literal if pruning
    #===========================================================================

    def _prune_literal_ifs(self) -> None:
        """Remove dead literal if/else branches from this module."""
        self.content = self._prune_literal_ifs_in_lines(self.content.copy())

    def _prune_literal_ifs_in_lines(self,
        lines: list[str]
    ) -> list[str]:
        """
        Return lines with dead if/else branches removed and kept branch bodies dedented.
        """
        pruned_content = []
        i = 0

        while i < len(lines):
            line = lines[i]
            match = self.IF_CONST_RE.match(line)

            if match is None:
                pruned_content.append(line)
                i += 1
                continue

            cond_value = match.group("value")

            then_start = i + 1
            then_end = self._find_matching_end(lines, i)
            then_body = lines[then_start:then_end]

            # Optional else block
            else_body = []
            next_idx = then_end + 1

            if next_idx < len(lines) and self.ELSE_BEGIN_RE.match(lines[next_idx]):
                else_start = next_idx + 1
                else_end = self._find_matching_end(lines, next_idx)
                else_body = lines[else_start:else_end]
                i = else_end + 1
            else:
                i = then_end + 1

            if cond_value == "1":
                pruned_content.extend(self._prune_literal_ifs_in_lines(
                    self._dedent_branch_body(then_body, line)
                ))
            elif cond_value == "0":
                pruned_content.extend(self._prune_literal_ifs_in_lines(
                    self._dedent_branch_body(else_body, line)
                ))
            else:
                raise AssertionError(f"Unexpected literal if value: {cond_value!r}")

        return pruned_content

    def _find_matching_end(self, lines: list[str], start_idx: int) -> int:
        """
        Helper method to find matching end for if-else block
        """

        depth = 1  # because start_idx is already "if (...) begin"

        for i in range(start_idx + 1, len(lines)):

            line = lines[i]

            depth += len(self.BEGIN_RE.findall(line))
            depth -= len(self.END_RE.findall(line))

            if depth == 0:
                return i

        raise ValueError(f"No matching end for if at line index {start_idx}")

    def _dedent_branch_body(self, body: list[str], if_line: str) -> list[str]:
        """
        Helper method to find matching end for if-else block
        """

        parent_indent = if_line[:len(if_line) - len(if_line.lstrip())]
        child_indent = parent_indent + "  "

        out = []
        for line in body:
            if line.startswith(child_indent):
                out.append(parent_indent + line[len(child_indent):])
            else:
                out.append(line)

        return out

    def prune_named_block(self, lines: list[str], block_name: str) -> list[str]:
        """
        prune specific block for debugging
        """

        out = []
        i = 0

        while i < len(lines):
            line = lines[i]
            match = self.NAMED_BEGIN_RE.match(line)

            if match is None or match.group("name") != block_name:
                out.append(line)
                i += 1
                continue

            block_end = self._find_matching_end(lines, i)
            block_body = lines[i + 1:block_end]

            out.append(line)  # keep "begin : initial_model"
            out.extend(self._prune_literal_ifs_in_lines(block_body))
            out.append(lines[block_end])  # keep matching "end"

            i = block_end + 1

        return out

    #===========================================================================
    # Dead declaration cleanup
    #===========================================================================

    def _remove_stale_declarations(self, max_iters: int = 20) -> None:
        """Remove references to parameters and variables that are no longer used"""

        for i in range(max_iters):
            print("clean up: ", i, " ", end="")

            old_content = self.content.copy()

            self._parse_declarations()
            self._remove_unreferenced_vars()
            # assumes that localparam declarations appear above all variabl declarations
            self._remove_unreferenced_localparams()

            if self.content == old_content:
                print("fix point")
                return
        raise RuntimeError("Unreferenced variables removal does not reach fixpoint")

    def _remove_unreferenced_localparams(self) -> int:
        """Remove dead localparam declarations."""

        identifier_counts = self._identifier_counts()

        unreferenced_params = [
            (param_name, line_num)
            for param_name, (_, _, line_num) in self.localparams.items()
            if identifier_counts[param_name] == 1
        ]

        unreferenced_params.sort(key=lambda x: x[1], reverse=True)

        for name, line_num in unreferenced_params:
            del self.content[line_num]
            del self.localparams[name]

        return len(unreferenced_params)

    def _remove_unreferenced_vars(self) -> None:
        """Remove dead variable declarations."""

        vars_usage = self._analyze_identifier_usage()

        lines_to_remove = set()

        vars_decl_to_remove_by_line: dict[int, list[str]] = defaultdict(list)

        for name, usage in vars_usage.items():

            if not usage["uses"]:
                vars_decl_to_remove_by_line[usage["declaration_line"]].append(name)
                for line_num in usage["assignments"]:
                    lines_to_remove.add(line_num)

        for line_num, vars_to_remove in vars_decl_to_remove_by_line.items():

            new_line = self._remove_declared_vars(self.content[line_num], vars_to_remove)

            # if newline is None, all variable declarations on this line were removed
            if new_line is None:
                lines_to_remove.add(line_num)
            # Override old line with newline with unused variables removed
            else:
                self.content[line_num] = new_line

        for line_num in sorted(lines_to_remove, reverse=True):
            del self.content[line_num]

    def _remove_declared_vars(self,
        line: str,
        vars_to_remove: set[str]
    ) -> str | None:

        match = self.DECLARATION_RE.match(line)
        assert match is not None, f"Invalid variable declaration line: {line}"

        indent, vars_type, var_names = match.groups()

        remaining_vars =[
            var_name.strip()
            for var_name in var_names.split(",")
            if var_name.strip() not in vars_to_remove
        ]

        if not remaining_vars:
            return None

        return f"{indent}{vars_type} {', '.join(remaining_vars)};\n"

    def _analyze_identifier_usage(self) -> dict[str, dict]:

        var_usage = {}

        for var_name, (var_type, dec_line) in self.vars.items():
            var_usage[var_name] = {
                'declaration_line': dec_line,
                'assignments': [],
                'uses': []
            }

        for line_num, line in enumerate(self.content):
            stripped = line.strip()
            code, _, _ = line.partition("//")
            code = code.rstrip("\n")

            # Check if assignment
            if match := self.ASSIGNMENT_RE.match(code):
                lhs = match.group('lhs')
                rhs = match.group('rhs')

                # Track LHS assignments
                if lhs in var_usage:
                    var_usage[lhs]['assignments'].append(line_num)

                for ident in set(self.IDENTIFIER_RE.findall(rhs)):
                    # if identifier is not a known variable skip
                    if ident not in var_usage:
                        continue
                    # don't count self-referential assignments as usage
                    if ident != lhs:
                        var_usage[ident]["uses"].append(line_num)

            else:
                # Skip declaration lines
                if stripped.startswith(('integer', 'real')):
                    continue

                for ident in set(self.IDENTIFIER_RE.findall(code)):
                    if ident in var_usage:
                        var_usage[ident]["uses"].append(line_num)

        return var_usage


    def _identifier_counts(self) -> Counter[str]:
        """
        Find all identifiers in the module and return a Counter of their counts.
        """
        counts: Counter[str] = Counter()

        for line in self.content:
            # don't count identifiers in comments
            code, _, _ = line.partition("//")
            counts.update(self.IDENTIFIER_RE.findall(code))

        return counts

#-------------------------------------------------------------------------------

class ExpressionEvaluator:

    NUM_LITERAL = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
    NUM_LITERAL_RE = re.compile(rf'^\s*{NUM_LITERAL}\s*$')

    IDENTIFIER = r'[A-Za-z_][A-Za-z0-9_$]*'
    IDENTIFIER_RE = re.compile(IDENTIFIER)

    SYSTEM_FUNC_REPLACEMENTS ={
        "$floor": "floor",
    }

    FUNCS = {
        "sqrt": math.sqrt,
        "pow" : pow,
        "exp" : math.exp,
        "log" : math.log,
        "ln"  : math.log,
        "sin" : math.sin,
        "cos" : math.cos,
        "tan" : math.tan,
        "abs" : abs,
        "min" : min,
        "max" : max,
        "floor": math.floor,
    }

    #---------------------------------------------------------------------------
    # Public class API

    @classmethod
    def substitute_constants(cls,
        expr: str,
        constants: Mapping[str, str],
    ) -> str:

        def replacement(match: re.Match):
            identifier = match.group(0)

            # if not a constant, return identifier as is
            if identifier not in constants:
                return identifier

            # if constant, replace identifier with constant value
            value = constants[identifier].strip()

            # sanity check that value is literal
            assert cls._is_numeric_literal(value), (
                f"Expected literal constant for {identifier !r}, got {value!r}"
            )

            # add parentheses around negative numbers
            if value.startswith("-"):
                value = f"({value})"

            return value

        return cls.IDENTIFIER_RE.sub(replacement, expr)

    @classmethod
    def try_eval_typed(cls,
        expr: str,
        value_type: str,
    ) -> str | None:
        """
        Try to evaluate expr as a constant.
        """
        expr = expr.strip()

        # fast path: plain literal
        if cls._is_numeric_literal(expr):
            if value_type == "real":
                # Real target accepts numeric literals as written.
                # Preserve source spelling to avoid noisy rewrites.
                return expr

            if value_type == "integer":
                # Integer target has conversion semantics.
                value = eval(expr, {"__builtins__": {}}, {})
                return cls._format_typed_value(value, value_type)

            raise ValueError(f"Unsupported value type {value_type!r}")

        value = cls._try_eval_raw_expr(expr)

        if value is None:
            return None

        return cls._format_typed_value(value, value_type)

    @classmethod
    def try_eval_cond(cls,
        expr: str,
    ) -> str | None:
        """
        Try to evaluate expr as a Verilog-A condition.
        """

        value = cls._try_eval_raw_expr(expr)

        if value is None:
            return None

        return cls._format_condition_value(value)

    #---------------------------------------------------------------------------
    # Private helper methods

    @classmethod
    def _is_numeric_literal(cls, expr: str) -> bool:
        return cls.NUM_LITERAL_RE.fullmatch(expr.strip()) is not None

    @staticmethod
    def _has_unsupported_syntax(
        expr: str
    ) -> bool:

        # add stuff here if neccesary

        return False

    @classmethod
    def _normalize_system_functions(cls, expr: str) -> str:
        if "$" not in expr:
            return expr

        for system_func, replacement in cls.SYSTEM_FUNC_REPLACEMENTS.items():
            expr = expr.replace(system_func, replacement)

        return expr

    @classmethod
    def _normalize_ternary_operators(cls, expr: str) -> str | None:
        """Convert Verilog-A ternary operators to Python conditional expressions."""

        while "?" in expr:
            expr = TernaryParser._replace_one_ternary(expr)

        assert "?" not in expr, (
            f"failed to replace all ternary operators: {expr}"
        )

        return expr

    @staticmethod
    def _normalize_logical_operators(
        expr: str
    ) -> str:
        """Convert Verilog-A logical operators to Python equivalents."""
        expr = expr.replace("&&", " and ").replace("||", " or ")
        # Replace ! with not, but NOT when followed by =
        # Negative lookahead (?!=) ensures we don't match !=
        expr = re.sub(r'!(?!=)', ' not ', expr)

        return expr

    @classmethod
    def _try_eval_raw_expr(cls,
        expr: str,
    ) -> int | float | bool | None:
        """
        Try to evaluate expr as a constant Python value.
        """

        expr = expr.strip()

        if cls._has_unsupported_syntax(expr):
            return None

        expr = cls._normalize_system_functions(expr)
        expr = cls._normalize_ternary_operators(expr)
        expr = cls._normalize_logical_operators(expr)

        try:
            value = eval(expr, {"__builtins__": {}}, cls.FUNCS)
        except (NameError,
                SyntaxError,
                TypeError,
                ValueError,
                ZeroDivisionError
            ):
            return None

        assert isinstance(value, int | float | bool), (
            f"Unexpected value type after eval: {type(value)}"
        )

        return value

    @staticmethod
    def _format_typed_value(
        value: int | float | bool,
        value_type: str,
    ) -> str:
        """
        Convert a fully evaluated expression value to Verilog-A to source literal
        for requested type
        """

        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"Infinite float value {value!r}")

        if value_type == "real":
            if isinstance(value, float):
                cast_value = value
            elif isinstance(value, bool):
                cast_value = 1.0 if value else 0.0
            elif isinstance(value, int):
                cast_value = float(value)
            else:
                assert False, f"Unexpected real value type {type(value)}"

        elif value_type == "integer":
            if isinstance(value, bool):
                cast_value = 1 if value else 0
            elif isinstance(value, int):
                cast_value = value
            elif isinstance(value, float):
                # Verilog-A rounds to nearest integer
                if value >= 0:
                    cast_value = math.floor(value + 0.5)
                else:
                    cast_value = math.ceil(value - 0.5)
            else:
                assert False, f"Unexpected integer value type {type(value)}"

        else:
            raise ValueError(f"Unsupported value type {value_type!r}")

        return repr(cast_value)

    @staticmethod
    def _format_condition_value(
        value: int | float | bool,
        ) -> str:
        """
        Convert a fully evaluated expression value to Verilog-A conditional literal
        """

        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"Invalid condition value {value!r}")

        if isinstance(value, bool):
            return "1" if value else "0"

        if isinstance(value, int | float):
            return "0" if value == 0 else "1"

        raise ValueError(f"Unexpected condition value type {type(value)}")


    # @classmethod
    # def _strip_outer_parens(expr: str) -> str:
    #     """
    #     Strip outer parentheses from expression.
    #     """
    #
    #     expr = expr.strip()
    #
    #     while expr.startswith("(") and expr.endswith(")"):
    #         depth = 0
    #         wraps_entire_expr = True
    #
    #         for i, char in enumerate(expr):
    #             if char == "(":
    #                 depth += 1
    #             elif char == ")":
    #                 depth -= 1
    #
    #                 if depth == 0 and i != len(expr) - 1:
    #                     wraps_entire_expr = False
    #                     break
    #
    #             if depth < 0:
    #                 wraps_entire_expr = False
    #                 break
    #
    #         if not wraps_entire_expr or depth != 0:
    #             break
    #
    #         expr = expr[1:-1].strip()
    #
    #     return expr

class TernaryParser:

    @classmethod
    def replace_all_ternaries(cls,
        expr: str,
    ) -> str | None:
        """
        Replace all ternaries, innermost first.
        """

        while "?" in expr:
            expr = cls._replace_one_ternary(expr)

        return expr

    @classmethod
    def _replace_one_ternary(cls,
        expr: str
    ) -> str | bool:

        # Find all ? operators
        q_positions = [
            i for i, ch in enumerate(expr)
            if ch == "?"
        ]

        # Find first replaceable leaf ternary
        for q in reversed(q_positions):

            ternary_start, ternary_end, cond, if_true, if_false = (
                cls._parse_ternary_at(expr, q)
            )

            # Only replace tenaries that do not contain other ternaries
            if "?" in cond or "?" in if_true or "?" in if_false:
                continue

            replacement = f"({if_true} if {cond} else {if_false})"

            return (
                    expr[:ternary_start]
                    + replacement
                    + expr[ternary_end + 1:]
            )

        return None

    @classmethod
    def _parse_ternary_at(cls,
        expr: str,
        q: int
    ) -> tuple[int, int, str, str, str] | None:

        # condition: parenthesized block before ?
        cond_end = cls._skip_ws_left(expr, q - 1)
        if cond_end < 0 or expr[cond_end] != ")":
            raise ValueError("expected ')' before '?'")

        cond_start = cls._match_left(expr, cond_end)

        # true branch: parenthesized block after ?
        true_start = cls._skip_ws_right(expr, q + 1)

        if true_start >= len(expr) or expr[true_start] != "(":
            raise ValueError("expected '(' after '?'")

        true_end = cls._match_right(expr, true_start)

        # colon after true branch
        colon = cls._skip_ws_right(expr, true_end + 1)
        if colon >= len(expr) or expr[colon] != ":":
            raise ValueError("expected ':' after true branch")

        # false branch: parenthesized block after :
        false_start = cls._skip_ws_right(expr, colon + 1)
        if false_start >= len(expr) or expr[false_start] != "(":
            raise ValueError("expected '(' after ':'")

        false_end = cls._match_right(expr, false_start)

        cond = expr[cond_start:cond_end + 1]
        if_true = expr[true_start:true_end + 1]
        if_false = expr[false_start:false_end + 1]

        return cond_start, false_end, cond, if_true, if_false

    @staticmethod
    def _skip_ws_left(s: str, i: int) -> int:
        while i >= 0 and s[i].isspace():
            i -= 1
        return i

    @staticmethod
    def _skip_ws_right(s: str, i: int) -> int:
        while i < len(s) and s[i].isspace():
            i += 1
        return i

    @staticmethod
    def _match_left(s: str, i: int) -> int:
        depth = 0

        while i >= 0:
            if s[i] == ")":
                depth += 1
            elif s[i] == "(":
                depth -= 1
                if depth == 0:
                    return i
            i -= 1

        raise ValueError("unmatched ')'")

    @staticmethod
    def _match_right(s: str, i: int) -> int:
        """i must point at '('."""
        depth = 0

        while i < len(s):
            if s[i] == "(":
                depth += 1
            elif s[i] == ")":
                depth -= 1
                if depth == 0:
                    return i
            i += 1

        raise ValueError("unmatched '('")


#-------------------------------------------------------------------------------
# Single transformation

def apply_prune_literals_if():

    dump = Path("sg13g2_moslv_rf_paramset_tt_tailored.dump.va")
    pp = PostPreproccesor(dump)
    pp.parse()

    new_dump = pp.apply_transforms(Transform.PRUNE_LITERAL_IFS)

    out = Path(dump.stem + ".pruned.va")
    out.write_text(new_dump)

def apply_rename_prune_literals_if():

    dump = Path("sg13g2_moslv_rf_paramset_tt_tailored.dump.va")
    pp = PostPreproccesor(dump)
    pp.parse()

    new_dump = pp.apply_transforms(
        [
            Transform.RENAME_LOCAL_VARS,
            Transform.PRUNE_LITERAL_IFS,
        ]
    )

    out = Path(dump.stem + ".renamed.pruned.va")
    out.write_text(new_dump)

def apply_rename_clean_prune_literals_if():

    dump = Path("sg13g2_moslv_rf_paramset_tt_tailored.dump.renamed.cleaned.va")
    pp = PostPreproccesor(dump)
    pp.parse()

    new_dump = pp.apply_transforms(Transform.PRUNE_LITERAL_IFS,)

    out = Path(dump.stem + ".pruned.va")
    out.write_text(new_dump)

def apply_rename():

    dump = Path("sg13g2_moslv_rf_paramset_tt_tailored.dump.va")
    pp = PostPreproccesor(dump)
    pp.parse()

    new_dump = pp.apply_transforms(Transform.RENAME_LOCAL_VARS)

    out = Path(dump.stem + ".renamed.va")
    out.write_text(new_dump)

def apply_remove_stale_declarations():

    dump = Path("sg13g2_moslv_rf_paramset_tt_tailored.dump.va")
    pp = PostPreproccesor(dump)
    pp.parse()

    new_dump = pp.apply_transforms(Transform.REMOVE_STALE_DECLARATIONS)

    out = Path(dump.stem + ".cleaned.va")
    out.write_text(new_dump)

#-------------------------------------------------------------------------------
# Double transformation

def apply_pruned_cleaned():

    dump = Path("sg13g2_moslv_rf_paramset_tt_tailored.dump.va")
    pp = PostPreproccesor(dump)
    pp.parse()

    new_dump = pp.apply_transforms([
            Transform.PRUNE_LITERAL_IFS,
            Transform.REMOVE_STALE_DECLARATIONS,
        ]
    )

    out = Path(dump.stem + ".pruned.cleaned.va")
    out.write_text(new_dump)

def apply_rename_clean():

    dump = Path("sg13g2_moslv_rf_paramset_tt_tailored.dump.va")
    pp = PostPreproccesor(dump)
    pp.parse()

    new_dump = pp.apply_transforms([
            Transform.RENAME_LOCAL_VARS,
            Transform.REMOVE_STALE_DECLARATIONS,
        ]
    )

    out = Path(dump.stem + ".renamed.cleaned.va")
    out.write_text(new_dump)



def apply_prune_if_literals_and_rename_local_vars():

    dump = Path("sg13g2_moslv_rf_paramset_tt_tailored.dump.va")
    pp = PostPreproccesor(dump)
    pp.parse()

    new_dump = pp.apply_transforms([
            Transform.PRUNE_LITERAL_IFS,
            Transform.RENAME_LOCAL_VARS,
        ]
    )

    out = Path(dump.stem + ".pruned.renamed.va")
    out.write_text(new_dump)


def apply_prune_if_literals_and_rename_local_vars_and_remove_stale_declarations():

    dump = Path("sg13g2_moslv_rf_paramset_tt_tailored.dump.va")
    pp = PostPreproccesor(dump)
    pp.parse()

    new_dump = pp.apply_transforms([
        Transform.PRUNE_LITERAL_IFS,
        Transform.RENAME_LOCAL_VARS,
        Transform.REMOVE_STALE_DECLARATIONS,
        ]
    )

    out = Path(dump.stem + ".pruned.renamed.cleaned.va")
    out.write_text(new_dump)

def run_optimize():

    dump = Path("sg13g2_moslv_rf_paramset_tt_tailored.dump.renamed.cleaned.pruned.va")
    pp = PostPreproccesor(dump)
    pp.parse()
    opt_dump = pp.optimize(already_prepared=True)

    out = Path(dump.stem + ".optimized.va")
    out.write_text(opt_dump)


if __name__ == '__main__':

    # apply_rename()

    # apply_rename_clean()
    # apply_prune_literals_if()
    # apply_rename_prune_literals_if()
    # apply_rename_clean()
    # apply_rename_clean_prune_literals_if()

    run_optimize()

    # apply_rename_local_vars()
    # apply_remove_stale_declarations()
    # apply_prune_if_literals_and_rename_local_vars()
    # apply_prune_if_literals_and_rename_local_vars_and_remove_stale_declarations()

    print("Finished")

