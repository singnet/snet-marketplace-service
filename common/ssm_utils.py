import boto3


def get_ssm_parameter(parameter):
    ssm = boto3.client('ssm')
    parameter = ssm.get_parameter(Name=parameter, WithDecryption=True)
    return parameter["Parameter"]["Value"]
