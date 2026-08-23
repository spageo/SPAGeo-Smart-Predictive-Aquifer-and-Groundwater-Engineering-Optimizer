"""Groundwater modeling engine using MODFLOW 6."""

import os
import tempfile
import numpy as np
from typing import Dict

import flopy

class ModelEngine:
    """MODFLOW 6 groundwater modeling engine."""

    def __init__(self):
        self.model = None
        self.simulation = None
        self.workspace = tempfile.mkdtemp()
        self.model_name = "spageo_model"

    def create_model(
            self,
            grid_config: Dict,
            boundary_conditions: Dict,
            aquifer_properties: Dict,
    ):
        """Create and configure the MODFLOW 6 groundwater model."""
        self.simulation = flopy.mf6.MFSimulation(
            sim_name=self.model_name,
            version="mf6",
            exe_name="mf6",
            sim_ws=self.workspace,
        )

        self.tdis = flopy.mf6.ModflowTdis(
            self.simulation,
            nper=1,
            perioddata=[(365.0, 1, 1.0)],
        )

        self.model = flopy.mf6.ModflowGwf(
            self.simulation,
            modelname=self.model_name,
        )

        self.ims = flopy.mf6.ModflowIms(
            self.simulation,
            complexity="SIMPLE",
        )

        self.simulation.register_ims_package(
            self.ims,
            [self.model.name],
        )

        self._setup_grid(grid_config)
        self._setup_boundary_conditions(boundary_conditions)
        self._setup_aquifer_properties(aquifer_properties)
        self._setup_initial_conditions({"initial_head": 10.0})
        self._setup_output_control()

        return self.simulation

    def _setup_grid(self, grid_config: Dict):
        """Configure the MODFLOW 6 model grid."""
        self.grid = flopy.mf6.ModflowGwfdis(
            self.model,
            nlay=grid_config["nlay"],
            nrow=grid_config["nrow"],
            ncol=grid_config["ncol"],
            delr=grid_config["cell_size_x"],
            delc=grid_config["cell_size_y"],
        )

        return self.grid

    def _setup_boundary_conditions(self, conditions: Dict):
        """Setup MODFLOW 6 boundary conditions."""
        if "recharge" in conditions:
            self.recharge = flopy.mf6.ModflowGwfrch(
                self.model,
                stress_period_data={
                    0: [
                        ((0, 0, 0), conditions["recharge"])
                    ]
                },
            )

        if "wells" in conditions:
            self.wells = flopy.mf6.ModflowGwfwel(
                self.model,
                stress_period_data=conditions["wells"],
            )

        return self.recharge if "recharge" in conditions else None

    def _setup_aquifer_properties(self, properties: Dict):
        """Setup aquifer properties."""
        self.npf = flopy.mf6.ModflowGwfnpf(
            self.model,
            save_flows=True,
            icelltype=properties.get("icelltype", 1),
            k=properties.get("k", 1.0),
            k33=properties.get("k33", 1.0),
        )

        return self.npf

    def _setup_initial_conditions(self, initial_conditions: Dict):
        """Setup MODFLOW 6 initial conditions."""
        self.initial_conditions = flopy.mf6.ModflowGwfic(
            self.model,
            strt=initial_conditions["initial_head"],
        )

        return self.initial_conditions

    def run_simulation(
        self,
        time_config: Dict,
        cloud: bool = False,
    ) -> Dict:
        """Run the groundwater simulation."""
        if cloud:
            return self._run_cloud_simulation(time_config)

        return self._run_local_simulation(time_config)

    def _run_local_simulation(self, time_config: Dict) -> Dict:
        """Run simulation locally."""
        self._configure_time_discretization(time_config)
        self._write_simulation()

        success, buff = self.simulation.run_simulation()

        if not success:
            raise RuntimeError("Simulation failed")

        return self._load_results()

    def _run_cloud_simulation(self, time_config: Dict) -> Dict:
        """Run simulation on cloud infrastructure."""
        # Implementation uses CloudManager
        # This will be detailed in Phase 5
        pass

    def _configure_time_discretization(self, time_config: Dict):
        """Configure MODFLOW 6 time discretization."""
        nper = time_config["nper"]
        perlen = time_config["perlen"]
        nstp = time_config["nstp"]
        tsmult = time_config["tsmult"]

        if not (
            len(perlen) == nper
            and len(nstp) == nper
            and len(tsmult) == nper
        ):
            raise ValueError(
                "perlen, nstp, and tsmult must each contain nper values"
            )

        perioddata = list(zip(perlen, nstp, tsmult))

        self.tdis.nper.set_data(nper)
        self.tdis.perioddata.set_data(perioddata)

        return self.tdis

    def _write_simulation(self):
        """Write MODFLOW 6 input files."""
        self.simulation.write_simulation()
        return self.workspace

    def _setup_output_control(self):
        """Configure MODFLOW 6 output control."""
        self.oc = flopy.mf6.ModflowGwfoc(
            self.model,
            budget_filerecord="spageo_model.cbc",
            head_filerecord="spageo_model.hds",
            saverecord=[("HEAD", "ALL"), ("BUDGET", "ALL")],
            printrecord=[("HEAD", "ALL"), ("BUDGET", "ALL")],
        )
        return self.oc

    def _load_results(self) -> Dict:
        """Load MODFLOW 6 simulation results."""
        head_file = os.path.join(self.workspace, f"{self.model_name}.hds")
        budget_file = os.path.join(self.workspace, f"{self.model_name}.cbc")

        if not os.path.isfile(head_file):
            raise FileNotFoundError(
                f"MODFLOW 6 head output not found: {head_file}"
            )

        if not os.path.isfile(budget_file):
            raise FileNotFoundError(
                f"MODFLOW 6 budget output not found: {budget_file}"
            )

        head = flopy.utils.HeadFile(head_file)
        budget = flopy.utils.CellBudgetFile(budget_file)

        return {
            "heads": head.get_data(),
            "budget": budget,
            "model_workspace": self.workspace,
        }

    def import_from_qgis(self, layer, field_mapping: Dict):
        """Import QGIS layer data for model boundary conditions."""
        pass

    def export_to_qgis(self, results: Dict):
        """Export simulation results as QGIS raster layers."""
        layers = {}

        if "heads" in results:
            raster = self._create_result_raster(
                     results["heads"],
                     "Heads",
                    )
            layers["heads"] = raster

        return layers

    def _create_result_raster(self, data, name: str):
        """Create QGIS raster from numpy array."""
        pass