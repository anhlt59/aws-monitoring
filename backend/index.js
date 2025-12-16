"use strict";
const url = require("url");
const https = require("https");
const querystring = require("querystring");

const BLUE_COLOR = "#0f6ebe";
const GREEN_COLOR = "#36a64f";
const RED_COLOR = "#ff0000";
const ORANGE_COLOR = "#f9a602";

// splitAndTrim
const splitAndTrim = function (string, separator) {
    return string.split(separator).filter(Boolean).map(string => string.trim());
}

const hookUrl = process.env.HOOK_URL;
const approvers = splitAndTrim(process.env.APPROVERS, ",");
const region = process.env.REGION;
const slackToken = process.env.SLACK_TOKEN;
const cmplusSlackToken = process.env.CMPLUS_SLACK_TOKEN;
const slackIdTeamsApproved = splitAndTrim(process.env.SLACK_ID_TEAMS_APPROVED, ",");
const slackVerificationToken = process.env.SLACK_VERIFICATION_TOKEN;
const cmplusSlackVerificationToken = process.env.CMPLUS_SLACK_VERIFICATION_TOKEN;
const stgAssumeRoleArn = process.env.STG_ASSUME_ROLE_ARN;
const prdAssumeRoleArn = process.env.PRD_ASSUME_ROLE_ARN;

const cmplusBatchStagingClusters = splitAndTrim(process.env.CMPLUS_BATCH_STAGING_CLUSTERS, ",");
const cmplusBatchStgImageNameSSMPath = process.env.CMPLUS_BATCH_STG_IMAGE_DEPLOY_SSM_PATH;
const cmplusBatchCodepipelineDeployName = process.env.CMPLUS_BATCH_CODEPIPELINE_DEPLOY_NAME;
const cmplusBatchSlackCallbackId = process.env.CMPLUS_BATCH_SLACK_CALLBACK_ID;
const cmplusBatchSlackChannel = process.env.CMPLUS_BATCH_SLACK_CHANNEL;

const cmplusAdminStagingClusters = splitAndTrim(process.env.CMPLUS_ADMIN_STAGING_CLUSTERS, ",");
const cmplusAdminStgImageNameSSMPath = process.env.CMPLUS_ADMIN_STG_IMAGE_DEPLOY_SSM_PATH;
const cmplusAdminCodepipelineDeployName = process.env.CMPLUS_ADMIN_CODEPIPELINE_DEPLOY_NAME;
const cmplusAdminSlackCallbackId = process.env.CMPLUS_ADMIN_SLACK_CALLBACK_ID;
const cmplusAdminSlackChannel = process.env.CMPLUS_ADMIN_SLACK_CHANNEL;

const cmplusApiStagingClusters = splitAndTrim(process.env.CMPLUS_API_STAGING_CLUSTERS, ",");
const cmplusApiStgImageNameSSMPath = process.env.CMPLUS_API_STG_IMAGE_DEPLOY_SSM_PATH;
const cmplusApiCodepipelineDeployName = process.env.CMPLUS_API_CODEPIPELINE_DEPLOY_NAME;
const cmplusApiSlackCallbackId = process.env.CMPLUS_API_SLACK_CALLBACK_ID;
const cmplusApiSlackChannel = process.env.CMPLUS_API_SLACK_CHANNEL;

const cmplusBatchThaStagingClusters = splitAndTrim(process.env.CMPLUS_BATCH_THA_STAGING_CLUSTERS, ",");
const cmplusBatchThaStgImageNameSSMPath = process.env.CMPLUS_BATCH_THA_STG_IMAGE_DEPLOY_SSM_PATH;
const cmplusBatchThaCodepipelineDeployName = process.env.CMPLUS_BATCH_THA_CODEPIPELINE_DEPLOY_NAME;
const cmplusBatchThaSlackCallbackId = process.env.CMPLUS_BATCH_THA_SLACK_CALLBACK_ID;
const cmplusBatchThaSlackChannel = process.env.CMPLUS_BATCH_THA_SLACK_CHANNEL;

const cmplusAdminThaStagingClusters = splitAndTrim(process.env.CMPLUS_ADMIN_THA_STAGING_CLUSTERS, ",");
const cmplusAdminThaStgImageNameSSMPath = process.env.CMPLUS_ADMIN_THA_STG_IMAGE_DEPLOY_SSM_PATH;
const cmplusAdminThaCodepipelineDeployName = process.env.CMPLUS_ADMIN_THA_CODEPIPELINE_DEPLOY_NAME;
const cmplusAdminThaSlackCallbackId = process.env.CMPLUS_ADMIN_THA_SLACK_CALLBACK_ID;
const cmplusAdminThaSlackChannel = process.env.CMPLUS_ADMIN_THA_SLACK_CHANNEL;

const cmplusApiThaStagingClusters = splitAndTrim(process.env.CMPLUS_API_THA_STAGING_CLUSTERS, ",");
const cmplusApiThaStgImageNameSSMPath = process.env.CMPLUS_API_THA_STG_IMAGE_DEPLOY_SSM_PATH;
const cmplusApiThaCodepipelineDeployName = process.env.CMPLUS_API_THA_CODEPIPELINE_DEPLOY_NAME;
const cmplusApiThaSlackCallbackId = process.env.CMPLUS_API_THA_SLACK_CALLBACK_ID;
const cmplusApiThaSlackChannel = process.env.CMPLUS_API_THA_SLACK_CHANNEL;

const cmplusApiNcStagingClusters = splitAndTrim(process.env.CMPLUS_API_NC_STAGING_CLUSTERS, ",");
const cmplusApiNcStgImageNameSSMPath = process.env.CMPLUS_API_NC_STG_IMAGE_DEPLOY_SSM_PATH;
const cmplusApiNcCodepipelineDeployName = process.env.CMPLUS_API_NC_CODEPIPELINE_DEPLOY_NAME;
const cmplusApiNcSlackCallbackId = process.env.CMPLUS_API_NC_SLACK_CALLBACK_ID;
const cmplusApiNcSlackChannel = process.env.CMPLUS_API_NC_SLACK_CHANNEL;

const checkEnvironmentVariables = [
    { CMPLUS_BATCH_STAGING_CLUSTERS: cmplusBatchStagingClusters },
    { CMPLUS_BATCH_STG_IMAGE_DEPLOY_SSM_PATH: cmplusBatchStgImageNameSSMPath },
    { CMPLUS_BATCH_CODEPIPELINE_DEPLOY_NAME: cmplusBatchCodepipelineDeployName },
    { CMPLUS_BATCH_SLACK_CALLBACK_ID: cmplusBatchSlackCallbackId },
    { CMPLUS_BATCH_SLACK_CHANNEL: cmplusBatchSlackChannel },
    { CMPLUS_ADMIN_STAGING_CLUSTERS: cmplusAdminStagingClusters },
    { CMPLUS_ADMIN_STG_IMAGE_DEPLOY_SSM_PATH: cmplusAdminStgImageNameSSMPath },
    { CMPLUS_ADMIN_CODEPIPELINE_DEPLOY_NAME: cmplusAdminCodepipelineDeployName },
    { CMPLUS_ADMIN_SLACK_CALLBACK_ID: cmplusAdminSlackCallbackId },
    { CMPLUS_ADMIN_SLACK_CHANNEL: cmplusAdminSlackChannel },
    { CMPLUS_API_STAGING_CLUSTERS: cmplusApiStagingClusters },
    { CMPLUS_API_STG_IMAGE_DEPLOY_SSM_PATH: cmplusApiStgImageNameSSMPath },
    { CMPLUS_API_CODEPIPELINE_DEPLOY_NAME: cmplusApiCodepipelineDeployName },
    { CMPLUS_API_SLACK_CALLBACK_ID: cmplusApiSlackCallbackId },
    { CMPLUS_API_SLACK_CHANNEL: cmplusApiSlackChannel },
    { CMPLUS_BATCH_THA_STAGING_CLUSTERS: cmplusBatchThaStagingClusters },
    { CMPLUS_BATCH_THA_STG_IMAGE_DEPLOY_SSM_PATH: cmplusBatchThaStgImageNameSSMPath },
    { CMPLUS_BATCH_THA_CODEPIPELINE_DEPLOY_NAME: cmplusBatchThaCodepipelineDeployName },
    { CMPLUS_BATCH_THA_SLACK_CALLBACK_ID: cmplusBatchThaSlackCallbackId },
    { CMPLUS_BATCH_THA_SLACK_CHANNEL: cmplusBatchThaSlackChannel },
    { CMPLUS_ADMIN_THA_STAGING_CLUSTERS: cmplusAdminThaStagingClusters },
    { CMPLUS_ADMIN_THA_STG_IMAGE_DEPLOY_SSM_PATH: cmplusAdminThaStgImageNameSSMPath },
    { CMPLUS_ADMIN_THA_CODEPIPELINE_DEPLOY_NAME: cmplusAdminThaCodepipelineDeployName },
    { CMPLUS_ADMIN_THA_SLACK_CALLBACK_ID: cmplusAdminThaSlackCallbackId },
    { CMPLUS_ADMIN_THA_SLACK_CHANNEL: cmplusAdminThaSlackChannel },
    { CMPLUS_API_THA_STAGING_CLUSTERS: cmplusApiThaStagingClusters },
    { CMPLUS_API_THA_STG_IMAGE_DEPLOY_SSM_PATH: cmplusApiThaStgImageNameSSMPath },
    { CMPLUS_API_THA_CODEPIPELINE_DEPLOY_NAME: cmplusApiThaCodepipelineDeployName },
    { CMPLUS_API_THA_SLACK_CALLBACK_ID: cmplusApiThaSlackCallbackId },
    { CMPLUS_API_THA_SLACK_CHANNEL: cmplusApiThaSlackChannel },
    { CMPLUS_API_NC_STAGING_CLUSTERS: cmplusApiNcStagingClusters },
    { CMPLUS_API_NC_STG_IMAGE_DEPLOY_SSM_PATH: cmplusApiNcStgImageNameSSMPath },
    { CMPLUS_API_NC_CODEPIPELINE_DEPLOY_NAME: cmplusApiNcCodepipelineDeployName },
    { CMPLUS_API_NC_SLACK_CALLBACK_ID: cmplusApiNcSlackCallbackId },
    { CMPLUS_API_NC_SLACK_CHANNEL: cmplusApiNcSlackChannel },
    { HOOK_URL: hookUrl },
    { APPROVERS: approvers },
    { REGION: region },
    { SLACK_TOKEN: slackToken },
    { SLACK_VERIFICATION_TOKEN: slackVerificationToken },
    { CMPLUS_SLACK_TOKEN: cmplusSlackToken },
    { CMPLUS_SLACK_VERIFICATION_TOKEN: cmplusSlackVerificationToken },
    { STG_ASSUME_ROLE_ARN: stgAssumeRoleArn },
    { PRD_ASSUME_ROLE_ARN: prdAssumeRoleArn },
    { SLACK_ID_TEAMS_APPROVED: slackIdTeamsApproved }
];

// AWS Config
const AWS = require("aws-sdk");
AWS.config.update({
    region: region,
    // accessKeyId: process.env.ACCESS_KEY_ID,
    // secretAccessKey: process.env.SECRECT_ACCESS_KEY
});

AWS.config.apiVersions = {
    apigatewayv2: "2018-11-29",
};

// Setup for staging account
const ecr = new AWS.ECR();
const ecs = new AWS.ECS();
const codepipeline = new AWS.CodePipeline();
const ssm = new AWS.SSM();

// Assume role
const sts = new AWS.STS();

// getCrossAccountCredentials
const getCrossAccountCredentials = async (roleArn) => {
    return new Promise((resolve, reject) => {
        try {
            const params = {
                RoleArn: roleArn,
                RoleSessionName: "awssdk"
            };
            sts.assumeRole(params, (err, data) => {
                if (err) {
                    callbackHandleErrorSendRequestToAWS(err, "sts.assumeRole");
                    reject(err);
                }
                if (data) {
                    callbackHandleSuccessSendRequestToAWS(data, "sts.assumeRole");
                    resolve(data);
                }
            });
        }
        catch (err) {
            console.error("getCrossAccountCredentials is failure \n", err);
            reject(err);
            return;
        }
    });
}

// updateConfigAWS
const updateConfigAWS = async (asssumeRoleData) => {
    return new Promise((resolve, reject) => {
        try {
            ecr.config.update({ accessKeyId: asssumeRoleData.Credentials.AccessKeyId, secretAccessKey: asssumeRoleData.Credentials.SecretAccessKey, sessionToken: asssumeRoleData.Credentials.SessionToken });
            ecs.config.update({ accessKeyId: asssumeRoleData.Credentials.AccessKeyId, secretAccessKey: asssumeRoleData.Credentials.SecretAccessKey, sessionToken: asssumeRoleData.Credentials.SessionToken });
            codepipeline.config.update({ accessKeyId: asssumeRoleData.Credentials.AccessKeyId, secretAccessKey: asssumeRoleData.Credentials.SecretAccessKey, sessionToken: asssumeRoleData.Credentials.SessionToken });
            ssm.config.update({ accessKeyId: asssumeRoleData.Credentials.AccessKeyId, secretAccessKey: asssumeRoleData.Credentials.SecretAccessKey, sessionToken: asssumeRoleData.Credentials.SessionToken });
            resolve();
        }
        catch (err) {
            console.error("updateConfigAWS is failure \n", err);
            reject(err);
            return;
        }
    });
}

// uniqueArray
const uniqueArray = function (array) {
    return [...new Set(array)];
}

// initBlock
const initBlock = function (environmentDeployment) {
    return {
        type: "section",
        text: {
            type: "mrkdwn",
            text: `*Deploy \`${environmentDeployment}\` ECS production by staging image.*`
        }
    }
};

// dividerBlock
const dividerBlock = {
    type: "divider"
};

// imagesBlock
const imagesBlock = function (options) {
    let block = {
        type: "input",
        block_id: "image_block",
        element: {
            action_id: "images_pick",
            type: "static_select",
            placeholder: {
                type: "plain_text",
                text: "Select Image"
            },
            options: options
        },
        label: {
            type: "plain_text",
            text: "Staging Image"
        }
    }
    return block;
};

// askForApproval
const askForApproval = function (params) {
    let mentionApprovers = [];
    for (let approver of params.approvers) {
        mentionApprovers.push(`<@${approver}>`)
    };

    let data = {
        channel: params.slackChannel,
        blocks: [
            {
                type: "section",
                block_id: "title_block",
                text: {
                    type: "mrkdwn",
                    text: `<@${params.requester}> is requesting a production deployment.`
                }
            },
            {
                type: "divider"
            },
            {
                type: "section",
                block_id: "environment",
                text: {
                    type: "mrkdwn",
                    text: `*Environment Deployment*`
                }
            },
            {
                type: "section",
                block_id: "environment_value",
                text: {
                    type: "mrkdwn",
                    text: `${params.environmentDeployment}`
                }
            },
            {
                type: "divider"
            },
            {
                type: "section",
                block_id: "image",
                text: {
                    type: "mrkdwn",
                    text: `*Deploy Image*`
                }
            },
            {
                type: "section",
                block_id: "image_value",
                text: {
                    type: "mrkdwn",
                    text: `${params.image}`
                }
            },
            {
                type: "divider"
            },
            {
                type: "section",
                block_id: "approvers",
                text: {
                    type: "mrkdwn",
                    text: `*Approvers*\n${mentionApprovers.join(" ")}`
                }
            },
            {
                type: "actions",
                block_id: "judgement_block",
                elements: [
                    {
                        action_id: "approved",
                        type: "button",
                        text: {
                            type: "plain_text",
                            text: "Approve",
                        },
                        style: "primary",
                        value: "approved"
                    },
                    {
                        action_id: "rejected",
                        type: "button",
                        text: {
                            type: "plain_text",
                            text: "Reject",
                        },
                        style: "danger",
                        value: "rejected"
                    }
                ]
            }
        ]
    }
    return data;
}


// initViewSlack
const initViewSlack = function (callbackId, blocks, environmentDeployment) {
    // view Slack
    let view = {
        type: "modal",
        callback_id: callbackId,
        title: {
            type: "plain_text",
            text: `Deploy ${environmentDeployment}`
        },
        close: {
            type: "plain_text",
            text: "Close"
        },
        submit: {
            type: "plain_text",
            text: "Submit"
        },
        blocks: blocks
    };
    return view;
};

//openViewSlack open the view Slack
const openViewSlack = async function (triggerId, view, slackToken) {
    return new Promise(async (resolve, reject) => {
        try {

            // Send loading view slack
            let slackMessageLoading = {
                "trigger_id": triggerId,
                "view": view
            };

            let data = await postMessage(slackMessageLoading, "https://slack.com/api/views.open", "application/json", "Bearer " + slackToken);
            let dataParse = JSON.parse(data);
            console.log("dataParse \n", dataParse);

            // Return if open view Slack fail
            if (!dataParse.view) {
                reject(new Error("Fail to open view Slack \n" + dataParse.response_metadata.messages));
                return;
            }
            resolve(dataParse.view.id);

        }
        catch (err) {
            console.error("openViewSlack is failure \n", err);
            reject(err);
            return;
        }
    });
};

//updateViewSlack update the view Slack
const updateViewSlack = async function (viewId, view, slackToken) {
    return new Promise(async (resolve, reject) => {
        try {
            // Update view
            let slackMessage = {
                "token": slackToken,
                "view_id": viewId,
                "view": view
            };

            let data = await postMessage(slackMessage, "https://slack.com/api/views.update", "application/json", "Bearer " + slackToken);
            let dataParse = JSON.parse(data);
            console.log("dataParse \n", dataParse);

            // Return if open view Slack fail
            if (!dataParse.view) {
                reject(new Error("Fail to open view Slack \n" + dataParse.response_metadata.messages));
                return;
            }
            resolve();
        }
        catch (err) {
            console.error("updateViewSlack is failure \n", err);
            reject(err);
            return;
        }
    });
};

// openInitViewSlack
const openInitViewSlack = async function (triggerId, callbackId, clusters, environmentDeployment, slackToken) {
    return new Promise(async (resolve, reject) => {
        try {
            // Send loading view slack
            let viewId = await openViewSlack(triggerId, initViewSlack(callbackId, [initBlock(environmentDeployment)], environmentDeployment), slackToken);

            // Update view
            let imagesBlock = await generateImagesBlockFromClusters(clusters);
            console.log("imagesBlock", imagesBlock)
            await updateViewSlack(viewId, initViewSlack(callbackId, [initBlock(environmentDeployment), dividerBlock, imagesBlock], environmentDeployment), slackToken);

            resolve();
        }
        catch (err) {
            console.error("openInitViewSlack is failure \n", err);
            reject(err);
            return;
        }
    });
};

// listImagesFromECRs
const listImagesFromECRs = async function (ecrs) {
    return new Promise(async (resolve, reject) => {
        try {
            let images = [];
            for (let ecr of ecrs) {
                let ecrData = {};
                // Check last page
                do {
                    if (ecrData.NextToken) {
                        ecrData = await listImagesECRAWS(ecr, ecrData.NextToken);
                    } else {
                        ecrData = await listImagesECRAWS(ecr);
                    }

                    // Get images
                    if (ecrData.imageIds.length != 0) {
                        for (let imageId of ecrData.imageIds) {
                            if (imageId.imageTag) {
                                images.push(`${ecr}:${imageId.imageTag}`)
                            }
                        }
                    }
                }
                while (ecrData.NextToken);
            }
            resolve(images);
        }
        catch (err) {
            console.error("listImagesFromECRs is failure \n", err);
            reject(err);
            return;
        }
    });
};

// getImagesFromClusters
const getImagesFromClusters = async function (clusters) {
    return new Promise(async (resolve, reject) => {
        try {
            let images = [];
            console.log("clusters", clusters);
            for (let cluster of clusters) {
                let taskArns = [];
                let dataOfListTasks = {};

                // Get task IDs from cluster
                do {
                    try {
                        // List tasks of ECS Cluster
                        if (dataOfListTasks.NextToken) {
                            dataOfListTasks = await listTasksOfECSCluster(cluster, dataOfListTasks.NextToken);
                        } else {
                            dataOfListTasks = await listTasksOfECSCluster(cluster);
                        }
                    }
                    catch (err) {
                        console.error(`listTasksOfECSCluster has error with ${cluster}. Contiune. `+err);
                        continue;
                    }

                    // Get task IDs
                    if (dataOfListTasks.taskArns.length != 0) {
                        for (let taskArn of dataOfListTasks.taskArns) {
                            if (taskArn) {
                                taskArns.push(taskArn);
                            }
                        }
                    }
                }
                while (dataOfListTasks.NextToken);

                // Get images from task Ids
                if (taskArns.length != 0) {
                    let dataOfDescribeTasks = await descibeTasksFromTaskIds(cluster, taskArns);
                    if (dataOfDescribeTasks.tasks.length != 0) {
                        for (let dataOfDescribeTask of dataOfDescribeTasks.tasks) {
                            if (dataOfDescribeTask) {
                                for (let container of dataOfDescribeTask.containers) {
                                    if (container) {
                                        images.push(container.image.split("/")[1]);
                                    }
                                }
                            }
                        }
                    }
                }
            }
            resolve(uniqueArray(images));
        }
        catch (err) {
            console.error("getImagesFromClusters is failure \n", err);
            reject(err);
            return;
        }
    });
};

// generateImagesBlockFromClusters
const generateImagesBlockFromClusters = async function (clusters) {
    return new Promise(async (resolve, reject) => {
        try {
            // Assume role
            let asssumeRoleData = await getCrossAccountCredentials(stgAssumeRoleArn);
            await updateConfigAWS(asssumeRoleData);

            // List images
            let images = await getImagesFromClusters(clusters);

            // Create options of block
            let options = [];
            for (let image of images) {
                if (image) {
                    options.push(
                        {
                            text: {
                                type: "plain_text",
                                text: image.trim().split(":")[1] // text must be less than 76 characters
                            },
                            value: image.trim()
                        }
                    );
                }
            }

            // Resolve block
            resolve(imagesBlock(options));
        }
        catch (err) {
            console.error("generateImagesBlockFromClusters is failure \n", err);
            reject(err);
            return;
        }
    });
};

// handleViewSubmission
const handleViewSubmission = async function (environmentDeployment, slackChannel, requester, image, slackToken) {
    return new Promise(async (resolve, reject) => {
        try {
            let params = {
                slackChannel: slackChannel,
                environmentDeployment: environmentDeployment,
                requester: requester,
                image: image,
                approvers: approvers
            };
            let slackMessage = askForApproval(params);
            let data = await postMessage(slackMessage, "https://slack.com/api/chat.postMessage", "application/json", "Bearer " + slackToken);
            console.log(data);
            resolve();
        }
        catch (err) {
            console.error("handleViewSubmission is failure \n", err);
            reject(err);
            return;
        }
    });
};

// handleApprovedBlockActions
const handleApprovedBlockActions = async function (eventPayload, slackToken) {
    return new Promise(async (resolve, reject) => {
        try {
            // Check approver
            if (!approvers.includes(eventPayload.user.id)) {
                console.log(`${eventPayload.user.username} is not approver.`);
                resolve();
            }

            // Update slack message
            let environmentDeployment = eventPayload.message.blocks.filter((block) => block.block_id == "environment_value")[0].text.text
            let imageDeployment = eventPayload.message.blocks.filter((block) => block.block_id == "image_value")[0].text.text
            let blocks = eventPayload.message.blocks.filter((block) => block.type != "actions")
            let approvedBlock = {
                type: "section",
                text: {
                    type: "mrkdwn",
                    text: `*<@${eventPayload.user.id}> has approved this request.*\n*Processing \`${environmentDeployment}\` production deployment.*`
                }
            };
            blocks.push(approvedBlock);
            let slackMessage = {
                channel: eventPayload.channel.id,
                blocks: blocks,
                ts: eventPayload.message.ts,
            }
            let data = await postMessage(slackMessage, "https://slack.com/api/chat.update", "application/json", "Bearer " + slackToken);
            console.log(data);

            // Process deployment
            switch (environmentDeployment) {
                case "cmplus-batch": {
                    console.log("environmentDeployment ", environmentDeployment, " cmplus-batch");
                    await processCmplusBatchProductionDeployment(imageDeployment);
                    break;
                }
                case "cmplus-admin": {
                    console.log("environmentDeployment ", environmentDeployment, " cmplus-admin");
                    await processCmplusAdminProductionDeployment(imageDeployment);
                    break;
                }
                case "cmplus-api": {
                    console.log("environmentDeployment ", environmentDeployment, " cmplus-api");
                    await processCmplusApiProductionDeployment(imageDeployment);
                    break;
                }
                case "cmplus-batch-tha": {
                    console.log("environmentDeployment ", environmentDeployment, " cmplus-batch-tha");
                    await processCmplusBatchThaProductionDeployment(imageDeployment);
                    break;
                }
                case "cmplus-admin-tha": {
                    console.log("environmentDeployment ", environmentDeployment, " cmplus-admin-tha");
                    await processCmplusAdminThaProductionDeployment(imageDeployment);
                    break;
                }
                case "cmplus-api-tha": {
                    console.log("environmentDeployment ", environmentDeployment, " cmplus-api-tha");
                    await processCmplusApiThaProductionDeployment(imageDeployment);
                    break;
                }
                case "cmplus-api-nc": {
                    console.log("environmentDeployment ", environmentDeployment, " cmplus-api-nc");
                    await processCmplusApiNcProductionDeployment(imageDeployment);
                    break;
                }
            }
            // console.log(`Process ${environmentDeployment} production deployment`);
            // await updateSSMParameterStore()

            resolve();
        }
        catch (err) {
            console.error("handleApprovedBlockActions is failure \n", err);
            reject(err);
            return;
        }
    });
};


// handleRejectedBlockActions
const handleRejectedBlockActions = async function (eventPayload, slackToken) {
    return new Promise(async (resolve, reject) => {
        try {
            // Check approver
            if (!approvers.includes(eventPayload.user.id)) {
                console.log(`${eventPayload.user.username} is not approver.`);
                resolve();
            }

            // Update slack message
            let blocks = eventPayload.message.blocks.filter((block) => block.type != "actions")
            let approvedBlock = {
                type: "section",
                text: {
                    type: "mrkdwn",
                    text: `*<@${eventPayload.user.id}> has \`rejected\` this request.*`
                }
            };
            blocks.push(approvedBlock);
            let slackMessage = {
                channel: eventPayload.channel.id,
                blocks: blocks,
                ts: eventPayload.message.ts,
            }
            let data = await postMessage(slackMessage, "https://slack.com/api/chat.update", "application/json", "Bearer " + slackToken);
            console.log(data);
            resolve();
        }
        catch (err) {
            console.error("handleRejectedBlockActions is failure \n", err);
            reject(err);
            return;
        }
    });
};

// processCmplusBatchProductionDeployment
const processCmplusBatchProductionDeployment = async function (imageName) {
    return new Promise(async (resolve, reject) => {
        try {
            // Assume role
            let asssumeRoleData = await getCrossAccountCredentials(prdAssumeRoleArn);
            await updateConfigAWS(asssumeRoleData);

            // Process
            await updateSSMParameterStore(cmplusBatchStgImageNameSSMPath, imageName);
            await startPipelineExecution(cmplusBatchCodepipelineDeployName);
            resolve();
        }
        catch (err) {
            console.error("processCmplusBatchProductionDeployment is failure \n", err);
            reject(err);
            return;
        }
    });
};

// processCmplusAdminProductionDeployment
const processCmplusAdminProductionDeployment = async function (imageName) {
    return new Promise(async (resolve, reject) => {
        try {
            // Assume role
            let asssumeRoleData = await getCrossAccountCredentials(prdAssumeRoleArn);
            await updateConfigAWS(asssumeRoleData);

            // Process
            await updateSSMParameterStore(cmplusAdminStgImageNameSSMPath, imageName);
            await startPipelineExecution(cmplusAdminCodepipelineDeployName);
            resolve();
        }
        catch (err) {
            console.error("processCmplusAdminProductionDeployment is failure \n", err);
            reject(err);
            return;
        }
    });
};

// processCmplusApiProductionDeployment
const processCmplusApiProductionDeployment = async function (imageName) {
    return new Promise(async (resolve, reject) => {
        try {
            // Assume role
            let asssumeRoleData = await getCrossAccountCredentials(prdAssumeRoleArn);
            await updateConfigAWS(asssumeRoleData);

            // Process
            await updateSSMParameterStore(cmplusApiStgImageNameSSMPath, imageName);
            await startPipelineExecution(cmplusApiCodepipelineDeployName);
            resolve();
        }
        catch (err) {
            console.error("processCmplusApiProductionDeployment is failure \n", err);
            reject(err);
            return;
        }
    });
};

// processCmplusBatchThaProductionDeployment
const processCmplusBatchThaProductionDeployment = async function (imageName) {
    return new Promise(async (resolve, reject) => {
        try {
            // Assume role
            let asssumeRoleData = await getCrossAccountCredentials(prdAssumeRoleArn);
            await updateConfigAWS(asssumeRoleData);

            // Process
            await updateSSMParameterStore(cmplusBatchThaStgImageNameSSMPath, imageName);
            await startPipelineExecution(cmplusBatchThaCodepipelineDeployName);
            resolve();
        }
        catch (err) {
            console.error("processCmplusBatchThaProductionDeployment is failure \n", err);
            reject(err);
            return;
        }
    });
};

// processCmplusAdminThaProductionDeployment
const processCmplusAdminThaProductionDeployment = async function (imageName) {
    return new Promise(async (resolve, reject) => {
        try {
            // Assume role
            let asssumeRoleData = await getCrossAccountCredentials(prdAssumeRoleArn);
            await updateConfigAWS(asssumeRoleData);

            // Process
            await updateSSMParameterStore(cmplusAdminThaStgImageNameSSMPath, imageName);
            await startPipelineExecution(cmplusAdminThaCodepipelineDeployName);
            resolve();
        }
        catch (err) {
            console.error("processCmplusAdminThaProductionDeployment is failure \n", err);
            reject(err);
            return;
        }
    });
};

// processCmplusApiThaProductionDeployment
const processCmplusApiThaProductionDeployment = async function (imageName) {
    return new Promise(async (resolve, reject) => {
        try {
            // Assume role
            let asssumeRoleData = await getCrossAccountCredentials(prdAssumeRoleArn);
            await updateConfigAWS(asssumeRoleData);

            // Process
            await updateSSMParameterStore(cmplusApiThaStgImageNameSSMPath, imageName);
            await startPipelineExecution(cmplusApiThaCodepipelineDeployName);
            resolve();
        }
        catch (err) {
            console.error("processCmplusApiThaProductionDeployment is failure \n", err);
            reject(err);
            return;
        }
    });
};

// processCmplusApiNcProductionDeployment
const processCmplusApiNcProductionDeployment = async function (imageName) {
    return new Promise(async (resolve, reject) => {
        try {
            // Assume role
            let asssumeRoleData = await getCrossAccountCredentials(prdAssumeRoleArn);
            await updateConfigAWS(asssumeRoleData);

            // Process
            await updateSSMParameterStore(cmplusApiNcStgImageNameSSMPath, imageName);
            await startPipelineExecution(cmplusApiNcCodepipelineDeployName);
            resolve();
        }
        catch (err) {
            console.error("processCmplusApiNcProductionDeployment is failure \n", err);
            reject(err);
            return;
        }
    });
};
// callbackHandleSuccessSendRequestToAWS
const callbackHandleSuccessSendRequestToAWS = function (data, requestName) {
    if (data) {
        console.log(`${requestName} is success \n`, data); // success
    }
};

// callbackHandleSuccessSendRequestToAWS
const callbackHandleErrorSendRequestToAWS = function (err, requestName) {
    if (err) {
        console.error(`${requestName} is failure \n`, err); // failure
    }
};

// listImagesECRAWS
const listImagesECRAWS = async function (repositoryName, nextToken) {
    return new Promise(async (resolve, reject) => {
        try {
            let params = {};
            if (nextToken) {
                params = {
                    NextToken: nextToken,
                    repositoryName: repositoryName
                };
            } else {
                params = {
                    repositoryName: repositoryName
                }
            }

            ecr.listImages(params, function (err, data) {
                if (err) {
                    callbackHandleErrorSendRequestToAWS(err, "ecr.listImages");
                    reject(err);
                }
                if (data) {
                    callbackHandleSuccessSendRequestToAWS(data, "ecr.listImages");
                    resolve(data);
                }
            });
        }
        catch (err) {
            console.error("listImagesECRAWS is failure \n", err);
            reject(err);
            return;
        }
    });
};

// listTasksOfECSCluster
const listTasksOfECSCluster = async function (clusterName, nextToken) {
    return new Promise(async (resolve, reject) => {
        try {
            let params = {};
            if (nextToken) {
                params = {
                    NextToken: nextToken,
                    cluster: clusterName
                };
            } else {
                params = {
                    cluster: clusterName
                }
            }

            ecs.listTasks(params, function (err, data) {
                if (err) {
                    callbackHandleErrorSendRequestToAWS(err, "ecs.listTasks");
                    reject(err);
                }
                if (data) {
                    callbackHandleSuccessSendRequestToAWS(data, "ecs.listTasks");
                    resolve(data);
                }
            });
        }
        catch (err) {
            console.error("listTasksOfECSCluster is failure \n", err);
            reject(err);
            return;
        }
    });
};

// descibeTasksFromTaskIds
const descibeTasksFromTaskIds = async function (cluster, taskIds, nextToken) {
    return new Promise(async (resolve, reject) => {
        try {
            let params = {};
            if (nextToken) {
                params = {
                    NextToken: nextToken,
                    cluster: cluster,
                    tasks: taskIds
                };
            } else {
                params = {
                    cluster: cluster,
                    tasks: taskIds
                }
            }

            ecs.describeTasks(params, function (err, data) {
                if (err) {
                    callbackHandleErrorSendRequestToAWS(err, "ecs.describeTasks");
                    reject(err);
                }
                if (data) {
                    callbackHandleSuccessSendRequestToAWS(data, "ecs.describeTasks");
                    resolve(data);
                }
            });
        }
        catch (err) {
            console.error("descibeTasksFromTaskIds is failure \n", err);
            reject(err);
            return;
        }
    });
};

// updateSSMParameterStore
const updateSSMParameterStore = async function (paramName, paramValue) {
    return new Promise(async (resolve, reject) => {
        try {
            let params = {
                Name: paramName, /* required */
                Value: paramValue, /* required */
                Description: paramName,
                Overwrite: true,
                Tier: "Standard",
                Type: "String"
            };
            ssm.putParameter(params, function (err, data) {
                if (err) {
                    callbackHandleErrorSendRequestToAWS(err, "ssm.putParameter");
                    reject(err);
                }
                if (data) {
                    callbackHandleSuccessSendRequestToAWS(data, "ssm.putParameter");
                    resolve(data);
                }
            });
        }
        catch (err) {
            console.error("updateSSMParameterStore is failure \n", err);
            reject(err);
            return;
        }
    });
};

// startPipelineExecution
const startPipelineExecution = async function (pipelineName) {
    return new Promise(async (resolve, reject) => {
        try {
            let params = {
                name: pipelineName, /* required */
            };
            codepipeline.startPipelineExecution(params, function (err, data) {
                if (err) {
                    callbackHandleErrorSendRequestToAWS(err, "codepipeline.startPipelineExecution");
                    reject(err);
                }
                if (data) {
                    callbackHandleSuccessSendRequestToAWS(data, "codepipeline.startPipelineExecution");
                    resolve(data);
                }
            });
        }
        catch (err) {
            console.error("startPipelineExecution is failure \n", err);
            reject(err);
            return;
        }
    });
};

// postMessage
const postMessage = async function (message, domainName, contentType, token) {
    return new Promise(async (resolve, reject) => {
        try {
            let body;
            if (contentType == "application/json") {
                body = JSON.stringify(message);
            }
            if (contentType == "application/x-www-form-urlencoded") {
                body = querystring.stringify(message);
            }
            let options = url.parse(domainName);
            options.method = "POST";
            options.headers = {
                "Authorization": token,
                "Content-Type": contentType,
                "Content-Length": Buffer.byteLength(body),
            };

            let postReq = https.request(options, function (res) {
                let chunks = [];
                res.setEncoding("utf8");
                res.on("data", function (chunk) {
                    return chunks.push(chunk);
                });
                res.on("end", function () {
                    let body = chunks.join("");
                    resolve(body);
                });

                if (res.statusCode < 400) {
                    console.log("Message posted!");
                } else if (res.statusCode < 500) {
                    console.error("4xx error occured when processing messages:" + res.statusCode + " - " + res.statusMessage);
                    reject(new Error("4xx error occured when processing messages:" + res.statusCode + " - " + res.statusMessage));
                    return;
                } else {
                    console.error("Server error when processing message: " + res.statusCode + " - " + res.statusMessage);
                    reject(new Error("Server error when processing message: " + res.statusCode + " - " + res.statusMessage));
                    return;
                }
                return res;
            });
            postReq.write(body);
            postReq.end();
        }
        catch (err) {
            console.error("postMessage is failure \n", err);
            reject(err);
            return;
        }
    });
};

// main process
const processFunction = async function (event) {
    return new Promise(async (resolve, reject) => {
        try {
            // print event
            console.log("event: \n", event);

            // Parse event
            let eventParse = JSON.parse(JSON.stringify(event, null, 2));
            console.log("eventParse: \n", eventParse);
            let eventBody = querystring.parse(eventParse.body);
            console.log("eventBody: \n", eventBody);
            let eventPayload;

            if (eventBody.payload) {
                eventPayload = JSON.parse(eventBody.payload);
                console.log("eventPayload: \n", JSON.stringify(eventPayload, null, 2));
            }

            if (eventBody.command == "/test-deploy") {
                console.log("eventBody.command", eventBody.command);
                return
            }

            // Verify request from Slack
            if (slackVerificationToken != eventPayload.token
                && cmplusSlackVerificationToken != eventPayload.token) {
                reject(new Error("Token is invalid."));
                return;
            }

            // Using slack token
            let slackTokenDynamic;
            if (slackVerificationToken == eventPayload.token) {
                slackTokenDynamic = slackToken;
            };

            if (cmplusSlackVerificationToken == eventPayload.token) {
                slackTokenDynamic = cmplusSlackToken;
            };

            // Check Slack Teams Approved
            if (!slackIdTeamsApproved.includes(eventPayload.team.id)) {
                reject(new Error(`${eventPayload.team.domain} Slack team is not approved.`));
                return;
            }

            switch (eventPayload.type) {
                case "shortcut": {
                    console.log("shortcut");
                    switch (eventPayload.callback_id) {
                        case cmplusBatchSlackCallbackId: {
                            console.log("cmplusBatchSlackCallbackId", cmplusBatchSlackCallbackId);
                            await openInitViewSlack(eventPayload.trigger_id, cmplusBatchSlackCallbackId, cmplusBatchStagingClusters, "cmplus-batch", slackTokenDynamic)
                            resolve(eventPayload);
                            return;
                        }
                        case cmplusAdminSlackCallbackId: {
                            console.log("cmplusAdminSlackCallbackId", cmplusAdminSlackCallbackId);
                            await openInitViewSlack(eventPayload.trigger_id, cmplusAdminSlackCallbackId, cmplusAdminStagingClusters, "cmplus-admin", slackTokenDynamic)
                            resolve(eventPayload);
                            return;
                        }
                        case cmplusApiSlackCallbackId: {
                            console.log("cmplusApiSlackCallbackId", cmplusApiSlackCallbackId);
                            await openInitViewSlack(eventPayload.trigger_id, cmplusApiSlackCallbackId, cmplusApiStagingClusters, "cmplus-api", slackTokenDynamic)
                            resolve(eventPayload);
                            return;
                        }
                        case cmplusBatchThaSlackCallbackId: {
                            console.log("cmplusBatchThaSlackCallbackId", cmplusBatchThaSlackCallbackId);
                            await openInitViewSlack(eventPayload.trigger_id, cmplusBatchThaSlackCallbackId, cmplusBatchThaStagingClusters, "cmplus-batch-tha", slackTokenDynamic)
                            resolve(eventPayload);
                            return;
                        }
                        case cmplusAdminThaSlackCallbackId: {
                            console.log("cmplusAdminThaSlackCallbackId", cmplusAdminThaSlackCallbackId);
                            await openInitViewSlack(eventPayload.trigger_id, cmplusAdminThaSlackCallbackId, cmplusAdminThaStagingClusters, "cmplus-admin-tha", slackTokenDynamic)
                            resolve(eventPayload);
                            return;
                        }
                        case cmplusApiThaSlackCallbackId: {
                            console.log("cmplusApiThaSlackCallbackId", cmplusApiThaSlackCallbackId);
                            await openInitViewSlack(eventPayload.trigger_id, cmplusApiThaSlackCallbackId, cmplusApiThaStagingClusters, "cmplus-api-tha", slackTokenDynamic)
                            resolve(eventPayload);
                            return;
                        }
                        case cmplusApiNcSlackCallbackId: {
                            console.log("cmplusApiNcSlackCallbackId", cmplusApiNcSlackCallbackId);
                            await openInitViewSlack(eventPayload.trigger_id, cmplusApiNcSlackCallbackId, cmplusApiNcStagingClusters, "cmplus-api-nc", slackTokenDynamic)
                            resolve(eventPayload);
                            return;
                        }
                    }
                    break;
                }

                case "view_submission": {
                    console.log("view_submission");
                    switch (eventPayload.view.callback_id) {
                        case cmplusBatchSlackCallbackId: {
                            console.log("cmplusBatchSlackCallbackId", cmplusBatchSlackCallbackId);
                            await handleViewSubmission("cmplus-batch", cmplusBatchSlackChannel, eventPayload.user.id, eventPayload.view.state.values.image_block.images_pick.selected_option.value, slackTokenDynamic);
                            resolve(eventPayload);
                            return;
                        }
                        case cmplusAdminSlackCallbackId: {
                            console.log("cmplusAdminSlackCallbackId", cmplusAdminSlackCallbackId);
                            await handleViewSubmission("cmplus-admin", cmplusAdminSlackChannel, eventPayload.user.id, eventPayload.view.state.values.image_block.images_pick.selected_option.value, slackTokenDynamic);
                            resolve(eventPayload);
                            return;
                        }
                        case cmplusApiSlackCallbackId: {
                            console.log("cmplusApiSlackCallbackId", cmplusApiSlackCallbackId);
                            await handleViewSubmission("cmplus-api", cmplusApiSlackChannel, eventPayload.user.id, eventPayload.view.state.values.image_block.images_pick.selected_option.value, slackTokenDynamic);
                            resolve(eventPayload);
                            return;
                        }
                        case cmplusBatchThaSlackCallbackId: {
                            console.log("cmplusBatchThaSlackCallbackId", cmplusBatchThaSlackCallbackId);
                            await handleViewSubmission("cmplus-batch-tha", cmplusBatchThaSlackChannel, eventPayload.user.id, eventPayload.view.state.values.image_block.images_pick.selected_option.value, slackTokenDynamic);
                            resolve(eventPayload);
                            return;
                        }
                        case cmplusAdminThaSlackCallbackId: {
                            console.log("cmplusAdminThaSlackCallbackId", cmplusAdminThaSlackCallbackId);
                            await handleViewSubmission("cmplus-admin-tha", cmplusAdminThaSlackChannel, eventPayload.user.id, eventPayload.view.state.values.image_block.images_pick.selected_option.value, slackTokenDynamic);
                            resolve(eventPayload);
                            return;
                        }
                        case cmplusApiThaSlackCallbackId: {
                            console.log("cmplusApiThaSlackCallbackId", cmplusApiThaSlackCallbackId);
                            await handleViewSubmission("cmplus-api-tha", cmplusApiThaSlackChannel, eventPayload.user.id, eventPayload.view.state.values.image_block.images_pick.selected_option.value, slackTokenDynamic);
                            resolve(eventPayload);
                            return;
                        }
                        case cmplusApiNcSlackCallbackId: {
                            console.log("cmplusApiNcSlackCallbackId", cmplusApiNcSlackCallbackId);
                            await handleViewSubmission("cmplus-api-nc", cmplusApiNcSlackChannel, eventPayload.user.id, eventPayload.view.state.values.image_block.images_pick.selected_option.value, slackTokenDynamic);
                            resolve(eventPayload);
                            return;
                        }
                    }
                    break;
                }

                case "block_actions": {
                    console.log("block_actions");
                    switch (eventPayload.actions[0].value) {
                        case "approved": {
                            console.log("approved");
                            await handleApprovedBlockActions(eventPayload, slackTokenDynamic);
                            resolve(eventPayload);
                            return;
                        }
                        case "rejected": {
                            console.log("rejected");
                            await handleRejectedBlockActions(eventPayload, slackTokenDynamic);
                            resolve(eventPayload);
                            return;
                        }
                    }
                    break;
                }

                // default case
                default: {
                    console.log("default case \n");
                }
            }

            resolve(eventPayload);
            return;
        }
        catch (err) {
            console.error("processFunction is failure \n", err);
            reject(err);
            return;
        }
    });
};

exports.handler = async function (event, context) {
    // console.log("Received event:", JSON.stringify(event, null, 2));
    try {
        // Check environment variable
        checkEnvironmentVariables.forEach(variable => {
            if (!Object.values(variable)[0]) {
                throw new Error("Missing environment variables. Please check: " + Object.keys(variable)[0]);
            }
        });

        // Get result from processFunction
        await processFunction(event);

        console.log("Lambda function is success");
        context.succeed();
        return;
    }
    catch (err) {
        console.error("exports.handler is failure \n" + err);

        // Send err to Slack
        let reportToSlack = `*Deploy Bot is failure:* \n` +
            `*- Error:* \`${err.message}\` \n`;
        console.log(reportToSlack);

        let color = RED_COLOR;
        let slackMessage = {};
        slackMessage.attachments = [
            {
                "color": color,
                "text": reportToSlack
            }
        ];
        await postMessage(slackMessage, hookUrl, "application/json", "");
        console.error("Lambda function is failure \n" + err);
        context.fail();
        return;
    }
};
