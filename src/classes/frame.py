from typing import List
from .section import Section, SectionFactory
from model.enums import BeamSide, ColumnSide
from model.validation import RegularFrameInput


class Frame:
    """
    Frame model class
    """
    element_avalable_id = 0

    def __init__(self, validated_frame : RegularFrameInput, section_factory: SectionFactory, damping : float = 0.05):
        """
        Instanciate a Frame object

        Args:
            validated_frame (RegularFrameInput): validated data model for frame
            damping (float, optional): critical damping ratio. Defaults to 0.05.
        """
        self.span_length = validated_frame.span_length             
        self.storey_height = validated_frame.storey_height        
        self.n_spans = validated_frame.n_spans
        self.n_storeys = validated_frame.n_storeys                    
        self.n_frames = validated_frame.n_frames
        self.masses = validated_frame.masses
        self.damping = damping  
        self.__section_factory = section_factory


    @property
    def height(self) -> float:
        return self.n_storeys * self.storey_height

    @property
    def length(self) -> float:     
        return self.n_spans * self.span_length

    @property
    def inelastic_shape(self) -> List[float]:
        shape = list()
        for storey in range(1, self.n_storeys + 1):
            if self.n_storeys <= 4:
                shape.append(storey * self.storey_height / self.height)
            
            else:
                shape.append(
                    4/3 * (storey * self.storey_height / self.height)
                    * (1 - 1/4 * storey * self.storey_height / self.height)
                )
            
        return shape

    @property
    def get_effective_height(self) -> float:
        shape = self.inelastic_shape
        heights = [
            storey * self.storey_height for storey in range(1, self.storey_height + 1)
        ]
        mass_displacement = [
            disp * mass for disp, mass in zip(shape, self.masses)
        ]
        mass_disp_heights = [
            mass_disp * height for mass_disp, height in zip(mass_displacement, heights)
        ]
        return sum(mass_disp_heights) / sum(mass_displacement)
    
    @property
    def get_effective_mass(self) -> float:
        shape = self.inelastic_shape()
        mass_displacement = [
            disp * mass for disp, mass in zip(shape, self.masses)
        ]
        mass2_displacement = [
            mass_disp * mass for mass_disp, mass in zip(mass_displacement, self.masses)
        ]
        return sum(mass_displacement)**2 / sum(mass2_displacement)

    @property
    def beam_sections(self) -> List[Section]:
        return self.__section_factory.beam_sections()

    @property
    def int_column_section(self) -> Section:
        return self.__section_factory.int_column_section()

    @property
    def ext_column_section(self) -> Section:
        return self.__section_factory.ext_column_section()

    @property
    def tendon_unbonded_length(self) -> float:
        return self.length + self.ext_column_section.h

    # Node functions
    def node_grid(self, vertical : int, storey : int) -> int:
        """
        Get the ID for a grid node

        Args:
            vertical (int): vertical of given node (0 - n_spans)
            storey (int): storey of given node (0 - n_storeys)

        Returns:
            int: node ID
        """
        assert 0 <= vertical <= self.n_spans , f"""
            vertical: {vertical} is not between 0 and {self.n_spans}
        """
        assert 0 <= storey <= self.n_storeys , f"""
            storey: {storey} is not between 0 and {self.n_storeys}
        """
        return (storey * (self.n_spans + 1)) + vertical

    def node_base(self, vertical : int) -> int:
        """
        Get the ID for a base node

        Args:
            vertical (int): vertical of given node (0 - n_spans)

        Returns:
            int: node ID
        """
        assert 0 <= vertical <= self.n_spans , f"""
            vertical: {vertical} is not between 0 and {self.n_spans}
        """
        return (self.n_storeys + 1) * (self.n_spans + 1) + vertical

    def node_panel(self, vertical : int, storey : int) -> int:
        """
        Get the ID for a panel node

        Args:
            vertical (int): vertical of given node (0 - n_spans)
            storey (int): storey of given node (1 - n_storeys)

        Returns:
            int: node ID
        """
        assert 0 <= vertical <= self.n_spans , f"""
            vertical: {vertical} is not between 0 and {self.n_spans}
        """
        assert 1 <= storey <= self.n_storeys , f"""
            storey: {storey} is not between 1 and {self.n_storeys}
        """
        return (self.n_storeys + storey + 1)*(self.n_spans + 1) + vertical

    def node_rigid_beam(self, vertical : int, storey : int, side : BeamSide) -> int:
        """
        Get the ID for a rigid beam node

        Args:
            vertical (int): vertical of given node (1 - n_spans)
            storey (int): storey of given node (1 - n_storeys)

        Returns:
            int: node ID
        """
        assert 1 <= vertical <= self.n_spans , f"""
            vertical: {vertical} is not between 1 and {self.n_spans}
        """
        assert 1 <= storey <= self.n_storeys , f"""
            storey: {storey} is not between 1 and {self.n_storeys}
        """
        return ((2*self.n_storeys + 1) * (self.n_spans + 1) 
                + self.n_spans * (2*storey - 1) 
                + 2*vertical 
                - (1 - side))

    def node_beam(self, vertical : int, storey : int, side : BeamSide) -> int:
        """
        Get the ID for a beam node

        Args:
            vertical (int): vertical of given node (1 - n_spans)
            storey (int): storey of given node (1 - n_storeys)

        Returns:
            int: node ID
        """
        assert 1 <= vertical <= self.n_spans , f"""
            vertical: {vertical} is not between 1 and {self.n_spans}
        """
        assert 1 <= storey <= self.n_storeys , f"""
            storey: {storey} is not between 1 and {self.n_storeys}
        """
        return ((2*self.n_storeys+ 1)*(2*self.n_spans + 1) 
                + 2*self.n_spans*(storey - 1) 
                + 2*vertical 
                - (1 - side))

    def node_column(self, vertical : int, storey : int, side : ColumnSide) -> int:
        """
        Get the ID for a column node

        Args:
            vertical (int): vertical of given node (0 - n_spans)
            storey (int): storey of given node (1 - (n_storeys - 1))

        Returns:
            int: node ID
        """
        assert 0 <= vertical <= self.n_spans , f"""
            vertical: {vertical} is not between 0 and {self.n_spans}
        """
        assert 1 <= storey <= (self.n_storeys - 1) , f"""
            storey: {storey} is not between 1 and {self.n_storeys - 1}
        """
        return (2*(vertical + (storey - 1) * (self.n_spans + 1) + self.n_spans * self.n_storeys + 1) 
                + (2*self.n_storeys + 1) * (2*self.n_spans + 1) 
                - (1 - side))

    def node_top_column(self, vertical : int) -> int: 
        """
        Get the ID for a top column node

        Args:
            vertical (int): vertical of given node (0 - n_spans)

        Returns:
            int: node ID
        """
        assert 0 <= vertical <= self.n_spans , f"""
            vertical: {vertical} is not between 0 and {self.n_spans}
        """
        return 4*self.n_storeys * (2*self.n_spans + 1) + vertical

    # Material functions
    def column_N(self, vertical : int) -> int:
        """
        Get the ID of the uniaxialMaterial of the N-link of a column

        Args:
            vertical (int): vertical of given link (0 - n_spans)

        Returns:
            int: material ID
        """
        if vertical == 0 or vertical == self.n_spans:
            return 1
        
        else:
            return 0

    def column_S(self, vertical : int) -> int:
        """
        Get the ID of the uniaxialMaterial of the S-link of a column

        Args:
            vertical (int): vertical of given link (0 - n_spans)

        Returns:
            int: material ID
        """
        if vertical == 0 or vertical == self.n_spans:
            return 3
        
        else:
            return 2

    def beam_PT(self, storey : int) -> int:
        """
        Get the ID of the uniaxialMaterial of the PT-link of a beam

        Args:
            storey (int): vertical of given link (1 - n_storeys)

        Returns:
            int: material ID
        """
        assert 1 <= storey <= self.n_storeys , f"""
            storey: {storey} is not between 1 and {self.n_storeys}
        """
        return 2*(storey + 1)

    def beam_S(self, storey : int) -> int:
        """
        Get the ID of the uniaxialMaterial of the S-link of a beam

        Args:
            storey (int): vertical of given link (1 - n_storeys)

        Returns:
            int: material ID
        """
        assert 1 <= storey <= self.n_storeys , f"""
            storey: {storey} is not between 1 and {self.n_storeys}
        """
        return 2*(storey + 1) + 1

    def joint_internal_link(self, storey : int) -> int:
        """
        Get the ID of the uniaxialMaterial of the panel link of an internal beam-column joint

        Args:
            storey (int): vertical of given link (1 - n_storeys)

        Returns:
            int: material ID
        """
        assert 1 <= storey <= self.n_storeys , f"""
            storey: {storey} is not between 1 and {self.n_storeys}
        """
        return 2*(self.n_storeys + 1) + (storey + 1)

    def joint_external_link(self, storey : int) -> int:
        """
        Get the ID of the uniaxialMaterial of the panel link of an external beam-column joint

        Args:
            storey (int): vertical of given link (1 - n_storeys)

        Returns:
            int: material ID
        """
        assert 1 <= storey <= self.n_storeys , f"""
            storey: {storey} is not between 1 and {self.n_storeys}
        """
        return 3*(self.n_storeys + 1) + storey

    def rigid_link(self) -> int:
        """
        Get the ID of the uniaxialMaterial of the rigid link

        Returns:
            int: material ID
        """
        return 4*(self.n_storeys + 1)

    def column_S_MinMax(self, vertical : int) -> int:
        """
        Get the ID of the uniaxialMaterial of the S-link of a column considering failure

        Args:
            vertical (int): vertical of given link (0 - n_spans)

        Returns:
            int: material ID
        """
        if vertical == 0 or vertical == self.n_spans:
            return 4*(self.n_storeys + 1) + 1
        
        else:
            return 4*(self.n_storeys + 1) + 2  

    def beam_S_MinMax(self, storey : int) -> int:
        """
        Get the ID of the uniaxialMaterial of the S-link of a beam considering failure

        Args:
            storey (int): vertical of given link (1 - n_storeys)

        Returns:
            int: material ID
        """
        assert 1 <= storey <= self.n_storeys , f"""
            storey: {storey} is not between 1 and {self.n_storeys}
        """
        return 4*(self.n_storeys + 1) + 2*(storey + 1) - 1

    def beam_PT_MinMax(self, storey : int) -> int:
        """
        Get the ID of the uniaxialMaterial of the PT-link of a beam considering failure

        Args:
            storey (int): vertical of given link (1 - n_storeys)

        Returns:
            int: material ID
        """
        assert 1 <= storey <= self.n_storeys , f"""
            storey: {storey} is not between 1 and {self.n_storeys}
        """
        return 4*(self.n_storeys + 1) + 2*(storey + 1) 

    def __str__(self) -> str:
        return f"""
        span lenght:  {self.span_length}m 
        storey height: {self.storey_height}m
        storeys: {self.n_storeys} 
        spans: {self.n_spans} 
        number of frames: {self.n_frames}
        damping: {self.damping} 
        floor masses: {self.masses}ton
        """
