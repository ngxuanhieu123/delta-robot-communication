from behave import given, when, then


@given("the coordinate transform object")
def given_the_coordinate_transform_object(context):
    context.transformer = CoordinateTransformer() 


@given("the vision's system position ({sys_x}, {sys_y}), the robot's system position ({robot_x}, {robot_y})")
def given_the_vision_system_position_and_the_robot_system_position(context, sys_x, sys_y, robot_x, robot_y):
    context.transformer.add_points([(int(sys_x), int(sys_y)), (int(robot_x), int(robot_y))])


@when("the transform system receives the input point ({input_x}, {input_y})")
def when_the_transform_system_give_the_position(context, input_x, input_y):
    context.result = context.transformer.convert((int(input_x), int(input_y)))


@then("the transform gives the result ({expected_x}, {expected_y})")
def then_the_result_should_match_with_the_expected_result(context, expected_x, expected_y):
    assert context.result == (int(expected_x), int(expected_y))
