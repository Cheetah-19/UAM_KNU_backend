from ..models import State


def stateExists(json_state):
    state = State.objects.filter(fato_in_UAM=json_state['fato_in_UAM'], path_in_UAM=json_state['path_in_UAM'],
                                       gate_UAM=json_state['gate_UAM'], path_out_UAM=json_state['path_out_UAM'],
                                       fato_out_UAM=json_state['fato_out_UAM'], gate_UAM_psg=json_state['gate_UAM_psg'],
                                       waiting_room_psg=json_state['waiting_room_psg'])

    if not state:
        return False
    else:
        return True
