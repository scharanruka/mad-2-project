# import os
# from werkzeug.utils import secure_filename


# def save_file(app, file, subfolder):
#     if file:
#         filename = secure_filename(file.filename)
#         folder = os.path.join(app.config["UPLOAD_FOLDER"], subfolder)
#         os.makedirs(folder, exist_ok=True)
#         path = os.path.join(folder, filename)
#         file.save(path)
#         return path
#     return None
