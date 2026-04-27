import cloudinary.uploader


def upload_image(file, folder='general'):
    result = cloudinary.uploader.upload(
        file,
        folder=f'wikala/{folder}',
        resource_type='image'
    )
    return result.get('secure_url')


def upload_document(file, folder='documents'):
    result = cloudinary.uploader.upload(
        file,
        folder=f'wikala/{folder}',
        resource_type='raw'
    )
    return result.get('secure_url')


def delete_file(public_id):
    result = cloudinary.uploader.destroy(public_id)
    return result.get('result') == 'ok'