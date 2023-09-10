/*
*This script scrapes (for now) images from a given Artstation likes page.
*It's not designed to save video files... yet.
*Due to ArtStation API limitations, only the first 50 projects are scanned and scraped.
*Existing files are not overwritten.
*DISCLAIMER: This script is for educational and personal non-profit use only! No AI is being trained with the downloaded images. Rather, the images obtained are primarily for more easily inspiring other artists and/or providing them with curated reference art on demand. A secondary purpose is archiving.
*WARNING: Repeated runs of this script in short timeframes WILL cause you to be IP banned from ArtStation if downloading large numbers of files (250+)! Space out your runs accordingly!
*Known issues:
* - large numbers of files downloaded (100+) seems to correlate with some of those files being corrupted
*/

"use strict";

var inputs = process.argv;
const fs = require('fs');
const client = require('https');
const rootPath = inputs[2];
const likesPageUrl = "https://www.artstation.com/users/" + inputs[3] + "/likes.json";
let fileRetrievalCounter = 0;
let prjCounter = 0;

//access JSON file at artstation.com/users/[uname]/likes.json as json
function fetchJSON(url) {
    return fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json'
        }

    })

        .then(response => response.json());
}

//function for creating new directories, combining a main rootPath with dirPath
const createDir = (dirPath) => {
    fs.mkdirSync(rootPath + "/" + dirPath, {recursive: true}, (error) => {
        if(error) {
            console.error('Encountered error: ', error);
        }
    });
    return rootPath + "/" + dirPath;
}

//downloads an image from a given url into the given filepath
function downloadImage(url, filepath) {
    return new Promise((resolve, reject) => {
        client.get(url, (result) => {
            if(result.statusCode === 200) {
                //console.log("writing new file...");
                setTimeout(function() {
                    result.pipe(fs.createWriteStream(filepath))
                    .on('error', reject)
                    .once('close', () => resolve(filepath));
                    console.log("   NEW FILE RETRIEVED: " + filepath);
                }, 2000);
                
            }
            else if(result.statusCode === 404 || result.statusCode === 403) {
                setTimeout(function() {
                    console.log("   ERROR: PROJECT NOT FOUND");
                }, 2000);
            }
            else {
                //Consume response data to free memory
                result.resume();
                reject(new Error(`Request failed with status code ${result.statusCode}`));
            }
        });
    });
}

/*
*formats a filename given the url
*this function is tailored to ArtStation's formatting of files
*thus, this function uses two phases of filename extraction/cleaning
*e.g. https://cdnb.artstation.com/p/assets/covers/images/.../large/johnsmith-mywork.jpg?0123456789 -> (phase1) johnsmith-mywork.jpg?0123456789 -> (phase 2) johnsmith-mywork.jpg
*/
function fileNameFormatter(url) {
    let cleanedNamePhase1 = url.split("/").slice(-1);
    //console.log(cleanedNamePhase1);
    let cleanedNamePhase2 = String(cleanedNamePhase1).split("?", 1).slice(0);
    //console.log(cleanedNamePhase2);
    return cleanedNamePhase2;
}

/*
*formats a file (directory) path, using the given artistName and projectTitle params
*e.g. "John Smith", "My Project" -> "John Smith/My Project"
*additionally, removes trailing spaces and undesirable characters (\/:*?"<>|) from both inputs
*/
function filePathFormatter(artistName, projectTitle) {
    let aName = artistName.replace(/[/\\?%*:.|"<>]/g, '_');
    let prjTitle = projectTitle.replace(/[/\\?%*:.|"<>]/g, '_');
    
    aName = aName.trim();
    prjTitle = prjTitle.trim();
    
    const paramsV = [aName, prjTitle];
    let path = paramsV.join("/");
    //console.log(path + ".");
    return path;
}

/*
*filePathFormatter helper function - check that artist name doesnt end with space
*/
function filePathFormatter_artistName_endsWithSpace(artistName) {
    if(artistName.endsWith(" ")){
        artistName = artistName.slice(0, -1);
    }
    return artistName;
}

/*
*filePathFormatter helper function - check that project title doesnt end with space
*/
function filePathFormatter_projectTitle_endsWithSpace(projectTitle) {
    if(projectTitle.endsWith(" ")){
        projectTitle = projectTitle.slice(0, -1);
    }
    return projectTitle;
}

/*
*formats a final file path by combining a directory path with a fileName
*/
function filePathFinalizer(dirPath, fileName) {
    const paramsV = [dirPath, fileName];
    let finalPath = paramsV.join("/");
    //console.log(finalPath);
    return finalPath;
}

/*
*creates a URL to a project's sekrit JSON file, allowing access to asset URLs
*/
function hashIDUrlMaker(hash_id) {
    const artstationProjectsUrl = "https://www.artstation.com/projects/";
    const extn = ".json";
    const paramsV = [artstationProjectsUrl, hash_id, extn];
    let finalUrl = paramsV.join("");
    //console.log(finalUrl);
    return finalUrl;
}

/*
*summarizes script run with tally of retrieved files and accessed projects, if any
*/
function summary(){
    setTimeout(function(){
        if(fileRetrievalCounter == 0) {
        console.log("No new files retrieved");
        }
        else {
            console.log("Retrieved " + fileRetrievalCounter + " file(s) from " + prjCounter + " project(s)");
        }
        console.log("Process complete. Goodbye!");
    }, (fileRetrievalCounter * 500) + (prjCounter * 1000));
}

/*
*where everything comes together...
*/
fetchJSON(likesPageUrl).then(function(result) {
    console.log("JSON fetched");
    if(result["total_count"] == 0){
        console.log("No projects available");
    }
    else {
        console.log("Checking for new projects...");
        for(let i = 0; i < result["data"].length; i++){

            let fullPath = createDir(filePathFormatter(result["data"][i]["user"]["full_name"], result["data"][i]["title"]))

            //create artstation.com/project/[hash_id].json
            let prjJSON = hashIDUrlMaker(result["data"][i]["hash_id"]);
            fetchJSON(prjJSON).then(function(result2) {
                let perPrjRetrievalCount = 0;
                for(let i = 0; i < result2["assets"].length; i++){

                    let imgUrl = result2["assets"][i]["image_url"];

                    var filePathNamed = filePathFinalizer(fullPath, fileNameFormatter(imgUrl));

                    //check that the file doesn't already exist, download it if not
                    if(!fs.existsSync(filePathNamed)) {
                        downloadImage(imgUrl, filePathNamed);
                        fileRetrievalCounter++;
                        perPrjRetrievalCount++;
                    }
                }
                if(perPrjRetrievalCount > 0){
                    prjCounter++;
                }
            });
        }
    }
    setTimeout(summary, (3000 + (fileRetrievalCounter * 500) + (prjCounter * 1000)));
});


