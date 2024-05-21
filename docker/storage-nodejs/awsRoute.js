'use strict';

const settings = require('./nodejs_settings.js');
const logger = require("./winston.js");
const { S3Client, PutObjectCommand  } = require("@aws-sdk/client-s3");
const multer = require("multer");
const fs = require('fs');
const { ALLOWED_FILE_TYPES } = require('./nodejs_settings.js');
const path = require('path');

const s3 = new S3Client({ region: settings.AWS_REGION });

const upload = multer({
  dest: 'uploads/',
  fileFilter: (req, file, cb) => {

    // Only allow certain file types - from settings
    const allowedFileTypesRegex = new RegExp(`\.(${settings.ALLOWED_FILE_TYPES})$`, 'i');
    if (!allowedFileTypesRegex.test(file.originalname)) {
      return cb(new Error(`Only files with specific extensions are allowed!`));
    }
    cb(null, true);
  }
});

async function sendToS3(req, res, next) {
  try {
    if (settings.DEBUG == 1) {
      logger.debug("aws sendToS3 POST triggered!!!!!!");
      logger.debug(JSON.stringify(req.body));
    }

    const file = await new Promise((resolve, reject) => {
      upload.single('file')(req, res, (err) => {
        if (err) {
          console.error(err);
          reject(err);
          //return res.status(400).json({ "status": false, "code": 400, "message": err });
        } else {
          resolve(req.file);
        }
      });
    });
    // temp filename
    console.log(file.filename)

    const customerId = req.body.customerId;
    let requestId = req.body.requestId ? req.body.requestId : 1;

    logger.info("aws sendToS3 file uploaded to node server for customer " + customerId);

    const uploadImage = async (file, customerId, source) => {
      const fileStream = fs.createReadStream(file.path);
      const originalFilename = file.originalname.replace(/ /g, "_");
      const now = new Date();
      const date = now.toISOString().slice(0, 10).replace(/-/g, '');
      // now.toISOString().slice(0, 19).replace(/[-T:]/g, '');
      const randomString = Math.random().toString(36).substring(2, 8);
      const filename = `${date}_${randomString}_${originalFilename}`;
      const fullS3Path = `${customerId}/assets/chat/${requestId}/${filename}`;

      const params = {
        Bucket: settings.AWS_S3_BUCKET,
        Key: fullS3Path,
        Body: fileStream,
        ACL: 'public-read',
      };

      const results = await s3.send(new PutObjectCommand(params));
      logger.debug(`Success, S3 file uploaded (${fullS3Path}). Result is ${JSON.stringify(results, null, 2)}`);

      fs.unlink(file.path, (err) => {
        logger.debug(`File deleted from node server (${file.path})`);
        if (err) {
          console.error(err);
        }
      });

      const fullPath = `https://${settings.AWS_S3_BUCKET}.s3.amazonaws.com/${fullS3Path}`;
      console.log(fullPath);
      return { filename: fullPath };
    }

    const s3UploadResult = await uploadImage(file, customerId);

    return res.status(200).json({ success: true, code: 200, message: s3UploadResult.filename });

  } catch (error) {
    if (settings.VERBOSE_SUPERB == 1) {
      console.log("Error", error);
    }
    console.log("Error", error);
    res.status(400).json({ "success": false, "code": 400, "message": "Error while uploading file to S3! " + error });
  }
}

module.exports.sendToS3 = sendToS3;