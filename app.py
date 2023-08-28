from flask import Flask, request, jsonify, session
import os
from flask_bcrypt import Bcrypt #pip install Flask-Bcrypt = https://pypi.org/project/Flask-Bcrypt/
from datetime import datetime, timedelta, timezone
from flask_cors import CORS, cross_origin #ModuleNotFoundError: No module named 'flask_cors' = pip install Flask-Cors
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, unset_jwt_cookies, jwt_required, JWTManager #pip install Flask-JWT-Extended
from models import db, User, Post
from werkzeug.utils import secure_filename #pip install Werkzeug
import json
from google.cloud import storage



firebase_credentials = {
  "type": "service_account",
  "project_id": "farmers2u-396909",
  "private_key_id": "085b1079767c7e424d3d6367201acafcff765e25",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCj7rza30Db29n8\nVtWInVwtERP843w3nfCJUEnGb9zCW3LWS4X46JBEH9Lmy9OklzV59lb8VoibknQl\nUOxiTgtZ/7c5t6trRWCCjC8BD0mBDGoMx1Ti0ICLAqwHgWtDexSPlaD8I6X883wb\nIVXvJwhJ2Oh/o5E5v6lvgxIAEwWnlOdymNpToFEa6vToIuUfTgNjudpPEDR4kr9b\nuk50t9hxjFE/3Yi1+nQ8+i1A+2/3QcsbxC4FjKtHy0bwnUsx5YaHSTaYTxOi+dxs\nQmMmoQj4dSPign5p8Kv56FYJq1YDw2DVsnBuox+c9cn3z3Ly5nMhlzA7qdfZ+Aj+\n5iFrke0XAgMBAAECggEAMwqy/70Sj0IpYcHRs7s3R4rxO8TC2PhSvBZlGiWbSWK6\n41FZkfIrdSKpgpYFPFKeYm6aj/ALkdDsW/AR4dvl+ew+aviupXRRA+TM/9n4K3en\nj3oDCqob0+yNjrqzoKuyb7CJkugwlw1i33mmLZPsJz4jyhYuMhpkkaVwVdiWYqJh\nSUkEPSbd6xC3mDsFQ0xMnTvZxQpOSp45pNYF+Z9fixdI0l1G1NII3mNQXvi5OMRA\npDn6USpgaDe3oSzpouF8TRhTpvaw43Xd1PQDBsvq1BQ9OIzNPQLLRiKZl6tVUrNe\ngcMNODxCPxRhzjAnF+qLCzZuRw9s7ouwxATqQt3FaQKBgQDORNztJE7hjVmfE8KB\nG6FfrXI0bfMEVsmEG5ZCi4YRfPJMy4pc/eonqHpqy4IBijmfAvDXmz6307oGjm+n\n7L3CEXbJLjnh5Iey65kXAY3p/BtehPwQOIpuEj68/Qph/KsXJL0ZXVrrfXx8Yojf\n9zpMr1mRa+JmMFCcIjwyfPOvSQKBgQDLdNOP6x/+FbexCXsTSRN4jfvVqsPvJx4k\nr7tuSr603Xg6EPmJOG0Qw3FKjoBvh7EU40d9pMb77tzObs4PqsLMQAS2pvTI1d2O\nLWRAtj2v0z55YqS5e0/E3ZI0Ipc+NasLSzs4M56mSLQWSymwyM3xPkbpGC8FWBMQ\nGmlBzhfZXwKBgQCZCZ6gk3+y+Ry1WgPFpqpkQlupaqoTXhDFY3JojPw7nWhocduG\ngx1nryikc7lRSyzVPWlTjmtKGFy84JEXFh70DeEEArgPUW8c4JAE8bJJGDN2PVSG\n9GxAnmjN7y/043JNCYUDfLAoaEIkRzcmdFdc7fyWWGTxTIeCUCQ5kVt7gQKBgD6N\nM4I64sImgSxP4uQCApd856FAeC7t0umqkbCOEGXg9Va840tZ6sZNoGYwu7IOgNYQ\nLmmloHvSa1aYYIgWkv9i61AQso+QmSZeNEVlAkAtbTa6qjRQgizfhlS7Ec7Rhz3Y\nqmNUE4HCNoPoJfAxPIfgAsMlaUd2VZ4M0LGnoFN3AoGBAKtObvjNr7pnqzICYaZf\n1/rKcdn6e7Ng0LAnDtQE3e10lDDo3oBLYOjP4Mn1Nm/JnnV4Wnus3uWan/HIe+j/\nqKX8ZDRDBKjsMtzPlZDZ2rqzlSFYsrAJnis2ZXuf8RImGoZKbuXc6gHnz1b/elVY\nIf6rLitSFeD+pju/rs2Sy0dI\n-----END PRIVATE KEY-----\n",
  "client_email": "farmers2u-cloud@farmers2u-396909.iam.gserviceaccount.com",
  "client_id": "103429868284965213206",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/farmers2u-cloud%40farmers2u-396909.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
    }
with open("firebase_credentials.json", "w") as write_file:
    json.dump(firebase_credentials, write_file)
service_account_json = os.environ.get("firebase_credentials.json")
storage_client = storage.Client.from_service_account_json(service_account_json)

bucket_name = 'image_storage_farmers2u'
bucket = storage_client.bucket(bucket_name)

default_logo_name = "farmers2u_logo.png"
default_logo = f"https://storage.googleapis.com/{bucket_name}/{default_logo_name}"


app = Flask(__name__)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

app.config['SECRET_KEY'] = 'farmers2u'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://uwzxsyhsydpgms:0192463d51b1cd4384bb291794b9cee8fb0aea8974dd00fc811b598c867e2f81@ec2-34-236-103-63.compute-1.amazonaws.com:5432/d1h5fpboqosunf'
 
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True
  
bcrypt = Bcrypt(app) 
CORS(app, supports_credentials=True)
db.init_app(app)
  
with app.app_context():
   db.create_all()

# migrate = Migrate(app, db)
from navbar_profile import getprofile_blueprint
app.register_blueprint(getprofile_blueprint)

from posts.routes import posts_blueprint
app.register_blueprint(posts_blueprint)

from posts.posts_sender import getposts_blueprint
app.register_blueprint(getposts_blueprint)

from posts.posts_filter import posts_filter_blueprint
app.register_blueprint(posts_filter_blueprint)

from posts.small_data import smalldata_blueprint
app.register_blueprint(smalldata_blueprint)

from posts.user_posts import userposts_blueprint
app.register_blueprint(userposts_blueprint)
 
from posts.updatePost import updatePost_blueprint
app.register_blueprint(updatePost_blueprint)

from busCard import business_blueprint
app.register_blueprint(business_blueprint)

from farmFilt import farmfilter_blueprint
app.register_blueprint(farmfilter_blueprint)


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
  
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def delete_object_by_url(url):
    if default_logo in url:
        return
    # Parse the URL to extract the object name
    object_name = url.split('/')[-1]

    # Initialize Google Cloud Storage client
    client = storage.Client.from_service_account_json(service_account_json)
    

    # Specify the bucket name
    bucket_name = 'image_storage_farmers2u'
    # Get the bucket
    bucket = client.bucket(bucket_name)

    # Delete the object (blob) with the extracted object name
    blob = bucket.blob(object_name)
    blob.delete()   

def generate_unique_filename(filename):
    from uuid import uuid4
    # Generate a unique filename by combining a random UUID and the original filename
    unique_filename = str(uuid4()) + '_' + filename
    return unique_filename

def check_file_exists(bucket_name, filename):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    return blob.exists()

def extract_filename_from_url(image_url):
    print("image_url", image_url)
    parts = image_url.split("/")
    filename = parts[-1]
    return filename

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/logintoken", methods=["POST"])
def create_token():
    email = request.json.get("email", None)
    #password = request.json.get("password", None)

    user = User.query.filter_by(email=email).first()

    # if email != "test" or password != "test":
    #    return {"msg": "Wrong rmail or password"}, 401
    
    # if user is None:
    #    return jsonify({"error": "Wrong email or password"}), 401
    
    if user is None:
        return jsonify({"error": "Wrong Email"}), 401
    
    #if not bcrypt.check_password_hash(user.password, password):
    #    return jsonify({"error": "Unauthorized"}), 401

    access_token = create_access_token(identity=email)
    #response = {"access_token": access_token}
    #return response

    return jsonify({
        "email": email,
        "userName": user.farm_name,
        "profilePicture": user.logo_picture,
        "access_token": access_token
    })


@app.route("/signup", methods=["POST"])
def signup():
    json_data = request.form.get('jsonData')
    data = json.loads(json_data)
    email = data.get("email")
    is_shipping = data.get("is_shipping")
    user_exists = User.query.filter_by(email=email).first() is not None
    if email == "":
        return jsonify({"error": "No email"}), 405
    if user_exists:
        return jsonify({"error": "Email already exists or None"}), 409
    if is_shipping is None:
        return jsonify({"success": "Valid email"})

    if 'files[]' not in request.files:
        logo_image_string = ""
        products_images_string = ""
        farm_images_string = ""
    else:
        logo_image = []
        products_images = []
        farm_images = []
        files = request.files.getlist('files[]')
        labels = request.form.getlist('labels[]')

        for i in range(len(files)):
            image_filename = generate_unique_filename(files[i].filename)
            blob = bucket.blob(image_filename)
            blob.upload_from_file(files[i])

            # Generate public URL for the uploaded image
            image_url = f"https://storage.googleapis.com/{bucket_name}/{image_filename}"

            if labels[i] == "1":
                logo_image.append(image_url)
            if labels[i] == "2":
                products_images.append(image_url)
            if labels[i] == "3":
                farm_images.append(image_url)

        logo_image_string = ','.join(logo_image)
        products_images_string = ','.join(products_images)
        farm_images_string = ','.join(farm_images)
        

        print(logo_image_string)
        print(products_images_string)
        print(farm_images_string)



    #if logo_picture:
    #    logo_picture_name = generate_unique_filename(logo_picture[0].filename)
    #    logo_picture[0].save(os.path.join('..', 'frontend', 'public', 'Form_images', 'Logo_image', logo_picture_name))

    google_name = data.get("google_name")
    # validation for new registered email
    google_profile_picture = data.get("google_profile_picture")
    google_family_name = data.get("google_family_name")
    shipping_distance = data.get("shipping_distance")
    is_shipping = data.get("is_shipping")
    opening_hours = data.get("opening_hours")
    closing_hours = data.get("closing_hours")
    types_of_products = data.get("types_of_products")
    #logo_picture = request.json["logo_picture"]
    #print("mumo")

    #logo_picture = request.json.get("logo_picture")
    #logo_picture_string = ','.join(str(photo) for photo in logo_picture)
    products_pictures = data.get("products_pictures")
    farm_pictures = data.get("farm_pictures")
    farm_name = data.get("farm_name")
    about = data.get("about")
    phone_number_official = data.get("phone_number_official")
    phone_number_whatsapp = data.get("phone_number_whatsapp")
    phone_number_telegram = data.get("phone_number_telegram")
    address = data.get("address")
    farmer_name = data.get("farmer_name")
    delivery_details = data.get("delivery_details")
    products = data.get("products")
    farm_site = data.get("farm_site")
    facebook = data.get("facebook")
    instagram = data.get("instagram")

    user_exists = User.query.filter_by(email=email).first() is not None
 
    if user_exists:
        return jsonify({"error": "Email already exists"}), 

    if logo_image_string == "":
        logo_image_string = default_logo
    
    #hashed_password = bcrypt.generate_password_hash(password)
    #new_user = User(name="tamir20",email=email, password=hashed_password, about="sample check")
    #new_user = User(name= "gilad", email=email, password=hashed_password, about="I am Gilad, a farmer.")
    new_user = User(email=email, google_profile_picture = google_profile_picture, google_name = google_name, 
                    google_family_name = google_family_name, shipping_distance = shipping_distance, 
                    is_shipping= is_shipping, opening_hours = opening_hours, closing_hours = closing_hours,  
                    logo_picture = logo_image_string, products_pictures = products_images_string,
                    farm_pictures = farm_images_string, farm_name = farm_name, about = about, types_of_products = types_of_products, 
                    phone_number_official = phone_number_official, phone_number_whatsapp = phone_number_whatsapp,
                    phone_number_telegram = phone_number_telegram, address = address, farmer_name = farmer_name,
                    delivery_details= delivery_details,products= products, farm_site = farm_site,
                    facebook = facebook, instagram = instagram)
    db.session.add(new_user)
    db.session.commit()
 
    #session["user_id"] = new_user.id
 
    return jsonify({
        "id": new_user.id,
        "email": new_user.email,
        "logo_picture": new_user.logo_picture
    })

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes = 30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                response.data = json.dumps(data)
        
        return response

    except (RuntimeError, KeyError):
        # no valid JWT
        return response
 
@app.route("/login", methods=["POST"])
def login_user():
    email = request.json["email"]
    #password = request.json["password"]
  
    user = User.query.filter_by(email=email).first()
  
    if user is None:
        return jsonify({"error": "Unauthorized Access"}), 401
  
    #if not bcrypt.check_password_hash(user.password, password):
    #    return jsonify({"error": "Unauthorized"}), 401
      
    session["user_id"] = user.id
  
    return jsonify({
        "id": user.id,
        "email": user.email
    })

@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@app.route('/profile/<getemail>')
@jwt_required() 
def my_profile(getemail):
    print(getemail)
    if not getemail:
        return jsonify({"error": "Unauthorized Access"}), 401
    user = User.query.filter_by(email=getemail).first()
    response_body = {
        "id": user.id,
        "google_profile_picture": user.google_profile_picture,
        "google_name": user.google_name,
        "google_family_name": user.google_family_name,
        "farmName": user.farmName,
        "about" : user.about,
        "phoneNumber_official": user.phone_number_official,
        "phoneNumber_whatsapp": user.phone_number_whatsapp,
        "phoneNumber_telegram": user.phone_number_telegram,
        "address" : user.address,
        "farmerName" : user.farmerName,
        "delivery_details" : user.delivery_details,
        "products" : user.products,
        "farm_site" : user.farm_site,
        "facebook" : user.facebook,
        "instagram" : user.instagram,
    }
  
    return response_body

@app.route('/settings/<getemail>')
@jwt_required() 
def my_settings(getemail):
    print(getemail)
    if not getemail:
        return jsonify({"error": "Unauthorized Access"}), 401
    user = User.query.filter_by(email=getemail).first()
    products_pictures = user.products_pictures.split(',')
    farm_pictures = user.farm_pictures.split(',')
    response_body = {
        "id": user.id,
        "google_profile_picture": user.google_profile_picture,
        "google_name": user.google_name,
        "google_family_name": user.google_family_name,
        "logo_picture": user.logo_picture,
        "farm_name": user.farm_name,
        "about" : user.about,
        "phone_number_official": user.phone_number_official,
        "phone_number_whatsapp": user.phone_number_whatsapp,
        "phone_number_telegram": user.phone_number_telegram,
        "address" : user.address,
        "farmer_name" : user.farmer_name,
        "delivery_details" : user.delivery_details,
        "products" : user.products,
        "farm_site" : user.farm_site,
        "facebook" : user.facebook,
        "instagram" : user.instagram,
        "is_shipping" : user.is_shipping,
        "shipping_distance" : user.shipping_distance,
        "products_images_list": products_pictures,
        "farm_images_list": farm_pictures,
        "opening_hours": user.opening_hours,
        "closing_hours": user.closing_hours,
        'types_of_products' : user.types_of_products
    }
  
    return response_body

@app.route('/settings/<getemail>', methods=["PUT"])
@jwt_required() 
def update_my_settings(getemail):
    print(getemail)
    if not getemail:
        return jsonify({"error": "Unauthorized Access"}), 401
    
    user = User.query.filter_by(email=getemail).first()
    json_data = request.form.get('jsonData')
    data = json.loads(json_data)
    print(data)
    user_posts = Post.query.filter_by(email=user.email).all()
    for post in user_posts:
        post.farmName = data.get("farm_name")
    # user.logo_picture = request.json['logo_picture']
    user.farm_name = data.get("farm_name")
    user.facebook = data.get('facebook')
    user.instagram = data.get('instagram')
    user.farm_site = data.get('farm_site')
    user.about = data.get('about')
    user.phone_number_official = data.get('phone_number_official')
    user.phone_number_whatsapp = data.get('phone_number_whatsapp')
    # user.phone_number_telegram = request.json['phone_number_telegram']
    user.address = data.get('address')
    user.farmer_name = data.get('farmer_name')
    user.delivery_details = data.get('delivery_details')
    user.products = data.get('products')
    user.is_shipping = data.get('is_shipping')
    user.shipping_distance = data.get('shipping_distance')
    user.opening_hours = data.get('opening_hours')
    user.closing_hours = data.get('closing_hours')
    user.types_of_products = data.get('types_of_products')
    labels = request.form.getlist('labels[]')
    print("labels",labels)
    if labels:
        for label in labels:
            if label == '4':
                # Delete logo images from the cloud
                if user.logo_picture:
                    delete_object_by_url(user.logo_picture)
                    user.logo_picture = default_logo  # Clear the list of URLs after deletion
                    for post in user_posts:
                        post.profilePicture = default_logo
            elif label == '5':
                if user.products_pictures:
                    # Delete product images from the cloud
                    urls = user.products_pictures.split(",")
                    for product_image_url in urls:
                        delete_object_by_url(product_image_url)
                    user.products_pictures = ""  # Clear the list of URLs after deletion
            elif label == '6':
                if user.farm_pictures:
                    # Delete farm images from the cloud
                    urls = user.farm_pictures.split(",")
                    for farm_image_url in urls:
                        delete_object_by_url(farm_image_url)
                    user.farm_pictures = ""  # Clear the list of URLs after deletion
    elements_to_remove = ['4','5','6']
    labels = [item for item in labels if item not in elements_to_remove]
    print("labelssss",labels)
    if 'files[]' not in request.files:
        None # do nothing
    else:
        products_images = []
        farm_images = []
        files = request.files.getlist('files[]')
        print("files", files)
        
        # Delete existing images from the cloud based on labels
        for label in labels:
            if label == '1':
                if user.logo_picture:
                    # Delete logo image from the cloud
                    delete_object_by_url(user.logo_picture)
                    user.logo_picture = default_logo
                    for post in user_posts:
                        post.profilePicture = default_logo
            elif label == '2':
                if user.products_pictures:
                    # Delete product images from the cloud
                    urls = user.products_pictures.split(",")
                    print("urls", urls)
                    for product_image_url in urls:
                        delete_object_by_url(product_image_url)
                    user.products_pictures = []  # Clear the list of URLs after deletion

            elif label == '3':
                if user.farm_pictures:
                    # Delete farm images from the cloud
                    urls = user.farm_pictures.split(",")
                    for farm_image_url in urls:
                        delete_object_by_url(farm_image_url)
                    user.farm_pictures = []  # Clear the list of URLs after deletion
            
        for i in range(len(files)):
            print("files:", files[i])
            image_filename = generate_unique_filename(files[i].filename)
            blob = bucket.blob(image_filename)
            blob.upload_from_file(files[i])

            # Generate public URL for the uploaded image
            image_url = f"https://storage.googleapis.com/{bucket_name}/{image_filename}"
            if labels[i] == "1":
                user.logo_picture = image_url
                for post in user_posts:
                    post.profilePicture = image_url
            elif labels[i] == "2":
                products_images.append(image_url)
            elif labels[i] == "3":
                print("farm_images", farm_images)
                farm_images.append(image_url)
        
        # Update products and farm images lists in the database
        if products_images:
            user.products_pictures = ','.join(products_images)
        if farm_images:
            user.farm_pictures = ','.join(farm_images)

    db.session.commit()

    return jsonify({
        "id": user.id,
        "profilePicture": user.logo_picture,
        "email": user.email
    })

 
if __name__ == "__main__":
    app.run(debug=True)
