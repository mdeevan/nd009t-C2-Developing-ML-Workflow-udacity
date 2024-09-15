#######################################################
################### SERIALIZE IMAGE
#######################################################


import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key    = event['s3_key']
    bucket = event['s3_bucket'] ## TODO: fill in
    
    copy_source = {
        'Bucket': bucket,
        'Key': key
    }
    
    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    # s3.copy_object(CopySource=copy_source, Key = "tmp/image.png" )

    # img = s3.download(Bucket = bucket, Key = "tmp/image.png")
    # image_data = base64.b64encode(img)
    # We read the data from a file


    s3.download_file(bucket, key, "/tmp/image.png")
    
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }



#######################################################
################### CLASSIFIER
#######################################################


import json
# import sagemaker
import base64
# from sagemaker.serializers import IdentitySerializer
import boto3

ENDPOINT = "image-classification-2024-09-15-03-21-40-077"

def lambda_handler(event, context):

    params    = event['body']
    image     = params['image_data']
    s3_bucket = params['s3_bucket']
    s3_key    = params['s3_key']


    # Decode the image data
    image = base64.b64decode(image) ## TODO: fill in)
    
    runtime = boto3.client("runtime.sagemaker")

    # # Instantiate a Predictor
    # predictor = sagemaker.Predictor ## TODO: fill in

    # # For this model the IdentitySerializer needs to be "image/png"
    # predictor.serializer = IdentitySerializer("image/png")
    
    # Make a prediction:
    # inferences = predictor.predict() ## TODO: fill in
    response = runtime.invoke_endpoint(
                                    EndpointName = ENDPOINT,
                                    ContentType  = "image/png",
                                    Body= image
                                    )
    
    # We return the data back to the Step Function    
    # event["inferences"] = inferences.decode('utf-8')
    inferences = json.loads(response['Body'].read().decode())
    event['inferences'] = inferences
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps(inferences)
    # }
    return {
        'statusCode': 200,
        'body': {
            "image_data": params['image_data'],
            "s3_bucket": s3_bucket,
            "s3_key": s3_key,
            "inferences": inferences
        }
    }

#######################################################
################### THRESHOLD
#######################################################

import json


THRESHOLD = .83

def lambda_handler(event, context):
    
    # Grab the inferences from the event
    data = event['body']
    inferences = data['inferences'] ## TODO: fill in
    

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = 1 if inferences[0]> THRESHOLD or inferences[1] > THRESHOLD else 0 ## TODO: fill in
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
    