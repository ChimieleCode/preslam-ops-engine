from functools import cache
import math
from dataclasses import dataclass, field
from typing import List
from model.validation import SectionCollectionInput

from .links import GMSteelLink, KineticLink, MultilinearElasticLink
from .material_classes import Timber, Tendon, Steel

@dataclass
class SectionLimitStates:
    """
    Dataclass containing section limit states expressed as gap openings
    """
    DS1: float     # failure of steel
    DS2: float     # yielding of tendon
    DST: float     # yielding of timber

@dataclass
class Section:
    """
    Dataclass containing the data of a section
    """
    n_tendons: int
    tendons_pt: float
    axial_load: float
    top_reinforcement_depth: float
    b: float
    h: float
    connection_stiffness_ratio: float
    reinforcement_diameter: int
    reinforcement_count: int
    lambda_bar: int
    timber: Timber = None
    steel: Steel = None
    tendon: Tendon = None
    multilinear_elastic_link: MultilinearElasticLink = None
    kinetic_link: KineticLink = None
    GM_link: GMSteelLink = None
    is_beam: bool = field(init=False)

    def __post_init__(self):
        if self.axial_load <= 1.:
            self.is_beam = True
        else:
            self.is_beam = False

    @property
    def area(self) -> float:
        return self.b * self.h
    
    @property
    def bottom_reinforcement_depth(self) -> float:
        return self.h - self.top_reinforcement_depth
    
    @property
    def inertia(self) -> float:
        return 1/12 * self.b * self.h**3

    @property
    def steel_area(self) -> float:
        return (1/4 * (self.reinforcement_diameter * 10**-3)**2 
                * math.pi * self.reinforcement_count)

    @property
    def post_tensioning_area(self) -> float:
        if self.is_beam:
            return self.tendon.A * self.n_tendons
        
        else:
            return 0
    
    @property
    def tendon_initial_strain(self) -> float:
        if self.is_beam:
            return self.tendons_pt / (self.post_tensioning_area * self.tendon.E)
        
        else:
            return 0
    
    @property
    def connection_stiffness(self) -> float:
        return self.timber.E * self.connection_stiffness_ratio
    
    @property
    def bar_length(self) -> float:
        return self.reinforcement_diameter * 10**-3 * self.lambda_bar/4
    
    def __repr__(self):
        return f"""
        section: {self.h}x{self.b}m (h x b)
        connection: {self.connection_stiffness_ratio}
        reinforcement: {self.reinforcement_count}f{self.reinforcement_diameter}
        top_depth: {self.top_reinforcement_depth}
        post-tensioning: {self.n_tendons}@{self.tendons_pt}kN
        axial load: {self.axial_load}kN
        timber: {self.timber}
        steel: {self.steel}
        tendon: {self.tendon}
        elastic link: {self.multilinear_elastic_link}
        kinetic link: {self.kinetic_link}
        GM plastic link: {self.GM_link}
        is it a beam: {self.is_beam}
        """


@dataclass(frozen=True)
class SectionFactory:
    """
    Dataclass responsable for the creation of section objects
    """
    validated_sections: SectionCollectionInput
    timber: Timber
    steel: Steel
    tendon: Tendon

    @cache
    def beam_sections(self) -> List[Section]:
        return [
            Section(
                timber=self.timber,
                tendon=self.tendon,
                steel=self.steel,
                **section.__dict__
            )
            for section in self.validated_sections.beams
        ]
    
    @cache
    def int_column_section(self) -> Section:
        if self.validated_sections.internal_column.n_tendons == 0:
            return Section(
                timber=self.timber,
                steel=self.steel,
                **self.validated_sections.internal_column.__dict__
            )
        else:
            return Section(
                tendon=self.tendon,
                timber=self.timber,
                steel=self.steel,
                **self.validated_sections.internal_column
            )

    @cache
    def ext_column_section(self) -> Section:
        if self.validated_sections.external_column.n_tendons == 0:
            return Section(
                timber=self.timber,
                steel=self.steel,
                **self.validated_sections.external_column.__dict__
            )
        else:
            return Section(
                tendon=self.tendon,
                timber=self.timber,
                steel=self.steel,
                **self.validated_sections.external_column
            )


    
