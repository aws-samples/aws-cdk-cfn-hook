#! /bin/bash
set -e
hook_base_folder_name="hooks"
for hook_holder in `ls ${hook_base_folder_name}`
do
    echo "Processing Folder ${hook_holder}"
    cd ${hook_base_folder_name}/${hook_holder}
    echo "Checking if .ignore file exists"
    if [ -f .ignore ]; then
      echo ".ignore file exists. Skipping"
    else
      failure_mode=$(cat parameter.json|jq .failure_mode)
      target_stack=$(cat parameter.json|jq .target_stack)
      export failure_mode target_stack
      echo "failure mode is set to: ${failure_mode}, target stack is set to: ${target_stack}"
      echo Executing cfn submit to register the hook
      cfn generate
      Hook_Name=$(cat .rpdk-config|jq .typeName)
      echo "Hook name is set to: ${Hook_Name}"
      cfn submit --set-default --role-arn ${hook_execution_role}
      HOOK_TYPE_ARN=$(aws cloudformation list-types --filters  "Category=REGISTERED,TypeNamePrefix=${Hook_Name}" |jq -r .TypeSummaries[0].TypeArn)
      export HOOK_TYPE_ARN
      echo $HOOK_TYPE_ARN
      aws cloudformation set-type-configuration \
      --configuration "{\"CloudFormationConfiguration\":{\"HookConfiguration\":{\"TargetStacks\":$target_stack,\"FailureMode\":$failure_mode}}}" \
      --type-arn $HOOK_TYPE_ARN
    fi
    cd ${CODEBUILD_SRC_DIR}
done