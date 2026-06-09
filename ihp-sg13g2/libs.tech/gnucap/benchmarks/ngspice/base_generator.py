#!/usr/bin/env python3
"""
Base generator class for ngspice SPICE netlist testbenches
"""
import shutil
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import List

from dirs import build_dir, PDK_LIBS_DIR

class ModelType(StrEnum):
    GENERIC = "generic"
    PARAMSET = "paramset"
    TAILORED_PARAMSET = "tailored_paramset"

class BaseNetlistGenerator(ABC):
    """
    Abstract base class for generating SPICE netlists for ngspice simulations.
    """

    def __init__(self):
        self.lines: List[str] = []

    def set_model_type(self, model_type: str):
        self.model_type = ModelType(model_type)

    def clean_build(self):
        # clean build
        for file in build_dir.glob("*.sp"):
            if file.is_file():
                file.unlink()

    @property
    @abstractmethod
    def title(self) -> str:
        """Return the title line for the SPICE netlist."""
        pass

    @property
    @abstractmethod
    def osdi_files(self) -> list[str]:
        """Return Osdis to bind"""
        return None

    @property
    @abstractmethod
    def includes(self) -> list[str]:
        """Return libs to include"""
        return None

    def options(self) -> dict[str, str]:
        """Return options."""
        return None

    def add_header(self) -> None:
        """Add standard header with title and model bindings."""
        self.lines.append(self.title)
        self.lines.append("")

    def add_includes(self) -> None:
        """Add .include statements."""

        for include in self.includes:
            self.lines.append(include)

        self.lines.append("")

    def add_options(self) -> None:
        """Add .options statements."""
        if self.options:
            for key, value in self.options.items():
                if value is None:
                    self.lines.append(f".options {key}")
                else:
                    self.lines.append(f".options {key}={value}")

            self.lines.append("")

    @abstractmethod
    def add_netlist(self):
        """Add netlist"""
        pass

    @abstractmethod
    def add_control_block(self) -> None:
        pass

    def add_end(self):
        self.lines.append("")
        self.lines.append(".end")

    def generate_netlist(self, net_name: str):

        self.net_name = net_name

        # Clear any existing lines
        self.lines = []
        self.add_header()
        self.add_includes()
        self.add_options()
        self.add_netlist()
        self.add_control_block()
        self.add_end()

        netlist_content = "\n".join(self.lines)
        netlist_filename = self.net_name + ".sp"

        with open(build_dir / netlist_filename, 'w') as f:
            f.write(netlist_content)

        print(f"Generated {self.net_name}")

        return netlist_filename

    def generate_spiceinit(self) -> None:

        lines = []

        lines.append(f"setcs sourcepath = ( $sourcepath {PDK_LIBS_DIR}/ngspice/models )")

        for osdi_file in self.osdi_files:
            lines.append(f"osdi '{PDK_LIBS_DIR}/ngspice/osdi/{osdi_file}'")

        lines.append("*printout suppression to improve performance")
        lines.append("option noacct nomod")

        spiceinit_content = "\n".join(lines)

        with open(build_dir / ".spiceinit", 'w') as f:
            f.write(spiceinit_content)

        return


