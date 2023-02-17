from aws_cdk import (
    # Duration,
    Stack,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    aws_iam as iam
)
import aws_cdk as cdk
from constructs import Construct
import os


class HookCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        deploy_input = codepipeline.Artifact()

        repo = codecommit.Repository(self, "Repository",
            repository_name="MyRepositoryNameHook",
            code=codecommit.Code.from_directory("repo","develop")
        )
        cdk.CfnOutput(self, "RepositoryName", value=repo.repository_name)
        hook_execution_role = iam.Role(self, "Role",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("resources.cloudformation.amazonaws.com"),
                iam.ServicePrincipal("hooks.cloudformation.amazonaws.com")
            )
        )
        hook_execution_role.add_to_policy(iam.PolicyStatement(
            actions=["*"],
            resources=["*"],
            effect=iam.Effect.DENY)
            )
        project = codebuild.Project(self, "MyProject",
        source=codebuild.Source.code_commit(repository=repo, branch_or_ref='develop'),
        environment=codebuild.BuildEnvironment(
            compute_type=codebuild.ComputeType.LARGE,
            privileged=True,
            build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_4,
            environment_variables={
                "hook_execution_role": codebuild.BuildEnvironmentVariable(
                    value=hook_execution_role.role_arn
                )
                }
        )
        )

        pipeline = codepipeline.Pipeline(self, "MyPipeline", enable_key_rotation=True)
        
        source_action = codepipeline_actions.CodeCommitSourceAction(
            action_name="CodeCommit",
            repository=repo,
            output=deploy_input,
            branch='develop'
        )

        build_action = codepipeline_actions.CodeBuildAction(
            action_name="Build_action",
            input=deploy_input,
            project=project
        )
        pipeline.add_stage(
            stage_name="Source",
            actions=[source_action]
        )

        pipeline.add_stage(
            stage_name="Build",
            actions=[build_action]
        )
        project.add_to_role_policy(iam.PolicyStatement(
            actions=["kms:EnableKeyRotation","kms:PutKeyPolicy","kms:Decrypt","kms:GenerateDataKey"],
            resources=["arn:aws:kms:"+ Stack.of(self).region + ":" + Stack.of(self).account + ":key/*"],
            effect=iam.Effect.ALLOW)
            )
        
        project.add_to_role_policy(iam.PolicyStatement(
            actions=["kms:CreateKey"],
            resources=["*"],
            effect=iam.Effect.ALLOW)
            )

        project.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudformation:DescribeType*","cloudformation:RegisterType","cloudformation:SetTypeDefaultVersion","cloudformation:ListTypes","cloudformation:SetTypeConfiguration"],
            resources=["*"],
            effect=iam.Effect.ALLOW)
            )
        LogAndMetricsDeliveryRole = "arn:aws:iam::" + Stack.of(self).account + ":role/CloudFormationManagedUplo-LogAndMetricsDeliveryRol*"
        Stack_Name = "arn:aws:cloudformation:" + Stack.of(self).region + ":" + Stack.of(self).account + ":stack/CloudFormationManagedUploadInfrastructure/*"

        project.add_to_role_policy(iam.PolicyStatement(
            actions=["iam:PassRole"],
            resources=[LogAndMetricsDeliveryRole,hook_execution_role.role_arn],
            effect=iam.Effect.ALLOW)
            )
        project.add_to_role_policy(iam.PolicyStatement(
            actions=["iam:CreateRole","iam:PutRolePolicy","iam:DeleteRolePolicy","iam:DeleteRole","iam:GetRolePolicy","iam:GetRole"],
            resources=[LogAndMetricsDeliveryRole],
            effect=iam.Effect.ALLOW)
            )
        project.add_to_role_policy(iam.PolicyStatement(
            actions=[
                "s3:CreateBucket",
                "s3:PutObject",
                "s3:PutEncryptionConfiguration",
                "s3:PutBucketLogging",
                "s3:PutLifecycleConfiguration",
                "s3:PutBucketAcl",
                "s3:PutBucketPolicy",
                "s3:PutBucketVersioning",
                "s3:GetObject"],
            resources=["arn:aws:s3:::cloudformationmanageduploadinfra*"],
            effect=iam.Effect.ALLOW)
            )
        project.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudformation:CreateStack","cloudformation:UpdateStack","cloudformation:DescribeStacks"],
            resources=[Stack_Name],
            effect=iam.Effect.ALLOW)
            )
