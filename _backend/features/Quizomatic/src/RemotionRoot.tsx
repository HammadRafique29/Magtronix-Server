import { Composition, staticFile, delayRender, continueRender } from 'remotion';
import { useEffect, useState } from 'react';
import useVideoData from './jsonFileReader'; // Import the custom hook
import { singleVideoGenerator } from './videoGenerator/single_video_temp';

export const RemotionRoot: React.FC = () => {
  const [durationInFrames, setDurationInFrames] = useState<number | null>(null);
  const [handle] = useState(() => delayRender());
  const defaultData = useVideoData(); // Fetch data using the custom hook

  useEffect(() => {
    const calculateDurations = async () => {
      if (!defaultData || !defaultData.videoData) return;

      try {
        const fps = 30;
        const totalDurationInSeconds = await defaultData.videoData.reduce(
          async (accPromise, video) => {
            const acc = await accPromise;
            const audioSources = [
              staticFile(video.questionAudio),
              staticFile(video.optionsAudio),
              staticFile(video.answerAudio),
            ];
            const audioDurations = await Promise.all(
              audioSources.map((src) => {
                const audio = new Audio(src);
                return new Promise<number>((resolve) => {
                  audio.addEventListener('loadedmetadata', () => {
                    resolve(audio.duration || 0);
                  });
                  audio.addEventListener('error', () => {
                    console.error(`Failed to load audio: ${src}`);
                    resolve(0); // Gracefully handle errors
                  });
                });
              })
            );

            return (
              acc + audioDurations[0] + audioDurations[1] + 11 + audioDurations[2] + 5
            );
          },
          Promise.resolve(0)
        );

        const totalDurationInFrames = Math.round(totalDurationInSeconds * fps);
        console.log('Total Duration in Frames:', totalDurationInFrames);
        setDurationInFrames(totalDurationInFrames || 30); // Fallback to 30 frames if calculation fails
      } catch (error) {
        console.error('Error calculating durations:', error);
        setDurationInFrames(30); // Fallback value
      }
    };

    if (defaultData) {
      calculateDurations(); // Call function to calculate duration based on data
    }
  }, [defaultData]); // Run when defaultData changes

  useEffect(() => {
    if (durationInFrames !== null && defaultData) {
      continueRender(handle); // Continue rendering once data is ready
    }
  }, [durationInFrames, defaultData, handle]); // Trigger when duration is calculated

  if (!defaultData || durationInFrames === null) {
    return <div>Loading...</div>; // Render a placeholder while loading
  }

  return (
    <>
      <Composition
        id="videoGenerator"
        component={singleVideoGenerator}
        durationInFrames={durationInFrames}
        fps={30}
        width={defaultData.width}
        height={defaultData.height}
        defaultProps={defaultData}
      />
    </>
  );
};
