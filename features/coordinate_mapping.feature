Feature: Coordinate Mapping from Vision system with the robot coordinate
    Scenario: The vision system's coordinate is match with the robot's coordinate
        Given the coordinate transform object
        Given the vision's system position (123, 50), the robot's system position (163, 50)
        And the vision's system position (50, 123), the robot's system position (90, 123)
        And the vision's system position (100, 100), the robot's system position (140, 100)
        When the transform system receives the input point (300, 300)
        Then the transform gives the result (340, 300)

