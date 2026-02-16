#include "my_bot_controller/simple_controller.hpp"


SimpleController::SimpleController(const std::string & name) 
 : Node(name)
{
    declare_parameter("wheel_radius", 0.033);
    declare_parameter("wheel_separation", 0.17);

    get_parameter("wheel_radius")

}