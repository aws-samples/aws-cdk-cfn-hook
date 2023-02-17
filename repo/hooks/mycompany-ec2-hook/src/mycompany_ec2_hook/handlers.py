import logging
from typing import Any, MutableMapping, Optional
from cloudformation_cli_python_lib import (
    BaseHookHandlerRequest,
    HandlerErrorCode,
    Hook,
    HookInvocationPoint,
    OperationStatus,
    ProgressEvent,
    SessionProxy,
    exceptions,
)

from .models import HookHandlerRequest, TypeConfigurationModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
TYPE_NAME = "MyCompany::EC2::Hook"

hook = Hook(TYPE_NAME, TypeConfigurationModel)
test_entrypoint = hook.test_entrypoint


@hook.handler(HookInvocationPoint.CREATE_PRE_PROVISION)
def pre_create_handler(
        session: Optional[SessionProxy],
        request: HookHandlerRequest,
        callback_context: MutableMapping[str, Any],
        type_configuration: TypeConfigurationModel
) -> ProgressEvent:
    target_model = request.hookContext.targetModel
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS
    )
    try:
        # Reading the Resource Hook's target properties
        resource_properties = target_model.get("resourceProperties");
        LOG.info("Logging the resource property");
        LOG.info("Resource Properties: " + str(resource_properties));
        LOG.info("EC2 being created with instance type: " + resource_properties['InstanceType']);
        LOG.info("Allowed EC2 instance type: " + type_configuration.instancetype);
        allowed_instance_type=type_configuration.instancetype.split(",")
        if resource_properties['InstanceType'] in  allowed_instance_type :
          LOG.info("SUCCESS. EC2 type matches");
          progress.status = OperationStatus.SUCCESS
        else:
          error_msg = "ERROR. EC2 type provided as: " + resource_properties['InstanceType'] + ". Allowed Type is " +type_configuration.instancetype
          LOG.info(error_msg);
          return ProgressEvent.failed(HandlerErrorCode.InternalFailure,error_msg )
    except Exception as e:
        raise exceptions.InternalFailure(f"{e}")
    return progress


