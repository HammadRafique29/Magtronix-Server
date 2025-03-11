import ffmpeg from 'fluent-ffmpeg';
import path from 'path';
import fs from 'fs';

// Type definition for the audio files
interface AudioFile {
  path: string;
  type: 'audio' | 'silence';
}

// Global array to store all audio and silence files
const audioFiles: AudioFile[] = [];

// Function to add an audio file to the list
function addAudioToList(audioPath: string): void {
  audioFiles.push({ path: audioPath, type: 'audio' });
}

// Function to add a silent slot (empty space)
function addEmptySlot(durationInSeconds: number): Promise<void> {
  return new Promise((resolve, reject) => {
    const silenceFile = path.join(__dirname, `silence_${durationInSeconds}s.wav`);

    ffmpeg()
      .input('anullsrc=r=44100:cl=stereo') // Generate silent audio
      .outputOptions(['-t', durationInSeconds.toString()]) // Set duration of silence
      .output(silenceFile)
      .on('end', () => {
        console.log(`Silence file created: ${silenceFile}`);
        audioFiles.push({ path: silenceFile, type: 'silence' });
        resolve();
      })
      .on('error', (err) => {
        console.error(`Error creating silence file: ${err}`);
        reject(err);
      })
      .run();
  });
}

// Function to merge audio files and silence slots
function mergeAudios(outputFilePath: string): void {
  const outputListFile = path.join(__dirname, 'audio_list.txt');
  const fileStream = fs.createWriteStream(outputListFile);

  audioFiles.forEach(file => {
    fileStream.write(`file '${file.path}'\n`);
  });

  fileStream.end();

  ffmpeg()
    .input(outputListFile)
    .inputOptions('-f concat')
    .inputOptions('-safe 0')
    .output(outputFilePath)
    .on('end', () => {
      console.log(`Merging completed! Final audio saved at: ${outputFilePath}`);
      fs.unlinkSync(outputListFile);
    })
    .run();
}



// Export the functions so they can be used elsewhere
export { addAudioToList, addEmptySlot, mergeAudios };
