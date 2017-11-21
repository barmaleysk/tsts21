from imgurpython import ImgurClient

client_id = ''
client_secret = ''
FILE_URL = "https://api.telegram.org/file/bot{0}/{1}"
client = ImgurClient(client_id, client_secret)
token = ''


def upload_image(image):
    return client.upload_from_url(FILE_URL.format(token, image))['link']
