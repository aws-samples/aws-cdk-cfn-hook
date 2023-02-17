#! /bin/bash
config_file="create_hook.json"
hook_base_folder_name="hooks"
if [ -f ${config_file} ]; then
  failure_mode=$(cat ${config_file}|jq -r .failure_mode)
  target_stack=$(cat ${config_file}|jq -r .target_stack)
  hook_name=$(cat ${config_file}|jq -r .hook_name)
  company_name=$(cat ${config_file}|jq -r .company_name)
  service_name=$(cat ${config_file}|jq -r .service_name)
  folder_name=${company_name}-${service_name}-${hook_name}
  lower_case_folder_name=$(echo "$folder_name" | tr '[:upper:]' '[:lower:]')
  echo "Creating folder: ${hook_base_folder_name}/${lower_case_folder_name}"
  if [ -d ${hook_base_folder_name}/${lower_case_folder_name} ];then
    echo "Hook folder ${hook_base_folder_name}/${company_name}-${service_name}-${hook_name} already exists. Skipping..."
  else
    mkdir ${hook_base_folder_name}/${lower_case_folder_name}
    cd ${hook_base_folder_name}/${lower_case_folder_name}
    echo yes | cfn init --type-name "$company_name::$service_name::$hook_name" --artifact-type "HOOK" python37
    jq -n --arg failure_mode ${failure_mode} --arg target_stack ${target_stack} '{"failure_mode":"\($failure_mode)","target_stack":"\($target_stack)"}' > parameter.json
  fi
else
  echo "${config_file} file does not exist. New hook creation is skipped"
fi