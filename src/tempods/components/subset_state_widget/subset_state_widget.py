from glue.core import ComponentID, Data
from glue.core.subset import AndState, CategorySubsetState, MaskSubsetState, RangeSubsetState, Subset, SubsetState
from glue_jupyter.view import Viewer
import ipyvuetify as v
from itertools import product
from numpy import indices, ndarray, unique
from traitlets import List, observe
from typing import Dict, Tuple

from cosmicds.utils import load_template


class SubsetStateWidget(v.VuetifyTemplate):
    template = load_template("subset_state_widget.vue", __file__, traitlet=True).tag(sync=True)
    size_options = List().tag(sync=True)
    size_selections = List().tag(sync=True)
    type_options = List().tag(sync=True)
    type_selections = List().tag(sync=True)

    def __init__(self, data: Data, viewer: Viewer):
        super().__init__()
        self.glue_data = data
        self.viewer = viewer
        self.type_att: ComponentID = data.id["PrimSource"]
        self.size_att: ComponentID = data.id["Size_binned"]
        
        self.type_options = list(unique(self.glue_data[self.type_att]))
        self.size_options = ["Small", "Medium", "Large"]
        self.indices = list(product(range(len(self.type_options)), range(len(self.size_options))))

        self._layer_indices = {}
        for (idx_t, idx_s) in self.indices:
            subset = data.new_subset()
            state = self._subset_state(idx_t, idx_s)
            subset.subset_state = state
            self.viewer.add_subset(subset)
            self._layer_indices[(idx_t, idx_s)] = len(self.viewer.layers) - 1

        self.type_selections = sorted(list(unique(data[self.type_att].codes)))
        self.size_selections = list(range(len(self.size_options)))

    def _type_state(self, type_index: int) -> CategorySubsetState:
        return CategorySubsetState(self.type_att, [type_index])
    
    def _size_state(self, size_index: int) -> RangeSubsetState:
        value = (size_index + 1) ** 2
        return RangeSubsetState(value, value, self.size_att)

    def _subset_state(self, type_index: int, size_index: int) -> AndState:
        return AndState(self._type_state(type_index), self._size_state(size_index))

    def _layer_index(self, type_index: int, size_index: int) -> int:
        return self._layer_indices[(type_index, size_index)]

    def _update_visibilities(self, type_indices: list[int], size_indices: list[int]):
        for t, s in self.indices:
            self.viewer.layers[self._layer_index(t, s)].state.visible = (t in type_indices) and (s in size_indices) 

    @observe('type_selections')
    def _on_type_selections_changed(self, change: dict):
        self._update_visibilities(change["new"], self.size_selections)
        
    @observe('size_selections')
    def _on_size_selections_changed(self, change: dict):
        self._update_visibilities(self.type_selections, change["new"])
