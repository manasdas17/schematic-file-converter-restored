""" 
Checks the following for the converted JSON:
    - has component component instances
    - component instances match up with a defined component
    - nets do not contain pins that don't exist
"""

def verify_json(data):
    """ 
    Checks the following for the converted JSON:
        - has component component instances
        - component instances match up with a defined component
        - nets do not contain pins that don't exist
    """
    assert ('component_instances' in data)
    assert (len(data['component_instances']) > 0)
    assert ('components' in data)

    # key is the instance id. value is the library id
    instance_and_lib = {}

    #make sure each instance's library id is defined as a component
    for instance in data['component_instances']:
        assert (instance['library_id'] in data['components'])
        instance_and_lib[instance['instance_id']] = instance['library_id']

    # key is the component name. value is the number of pins it has
    component_and_pins = {}

    for comp_id, comp in data['components'].iteritems():
        component_and_pins[comp_id] = []
        for symbol in comp['symbols']:
            for body in symbol['bodies']:
                for pin in body ['pins']:
                    component_and_pins[comp_id].append(pin['pin_number'])

    assert ('nets' in data)

    # check to make sure that a net doesn't have an instance with a pin number that
    # its component doesn't have
    for net in data['nets']:
        for point in net['points']:
            for comp in point['connected_components']:
                lib_id = instance_and_lib[comp['instance_id']]
                assert (comp['pin_number'] in component_and_pins[lib_id])
