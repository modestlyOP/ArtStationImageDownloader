/*
*This script accesses a given ArtStation project, and downloads each individual art asset (i.e. image) to the given directory.
*Video downloading is currently not supported, and any videos encountered will cause the script to download only their thumbnail.
*/

"use strict";

var inputs = process.argv;
const fs = require('fs');
const client = require('https');
const rootPath = inputs[2];
const prjURL = inputs[3];
let fileRetrievalCounter = 0;

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
                setTimeout(function(){
                    result.pipe(fs.createWriteStream(filepath))
                    .on('error', reject)
                    .once('close', () => resolve(filepath));
                    console.log("   NEW FILE RETRIEVED: " + filepath);
                }, 2000);
                
            }
            else if(result.statusCode == 404 || result.statusCode == 403) {
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

function extractHashID(url) {
    return String(url.split("artwork/").slice(-1)).replace(/[/\\?%*:.|"<>]/g, '');
}

/*
*creates a URL to a project's sekrit JSON file, allowing access to asset URLs
*/
function hashIDUrlMaker(url) {
    const hash_id = extractHashID(url);
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
            console.log("Retrieved " + fileRetrievalCounter + " file(s)");
        }
        console.log("Process complete. Goodbye!");
    }, (fileRetrievalCounter * 500));
}

/*
*where everything comes together...
*/
//create artstation.com/project/[hash_id].json
let prjJSON = hashIDUrlMaker(prjURL);
fetchJSON(prjJSON).then(function(result) {
    let fullPath = createDir(filePathFormatter(result["user"]["full_name"], result["title"]))
    //let perPrjRetrievalCount = 0;
    for(let i = 0; i < result["assets"].length; i++){

        let imgUrl = result["assets"][i]["image_url"];

        var filePathNamed = filePathFinalizer(fullPath, fileNameFormatter(imgUrl));

        //check that the file doesn't already exist, download it if not
        if(!fs.existsSync(filePathNamed)) {
            downloadImage(imgUrl, filePathNamed);
            fileRetrievalCounter++;
        }
    }
    setTimeout(summary, 3000 + (fileRetrievalCounter * 500));
});

