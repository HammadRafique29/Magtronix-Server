import { useEffect, useState } from 'react';
import { staticFile } from 'remotion';

interface VideoData {
    questionText: string;
    optionstext: string;
    answerText: string;
    questionAudio: string;
    optionsAudio: string;
    answerAudio: string;
    combinedAudio: string;
    backgroundImage: string;
}

interface DefaultData {
    template: string;
    videoCount: number;
    width: number;
    height: number;
    videoData: VideoData[];
}

const useVideoData = () => {
  const [data, setData] = useState<DefaultData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(staticFile('/assets/video_generation_data.json'));
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const fetchedData = await response.json();
        setData(fetchedData);
      } catch (error) {
        console.error('Error fetching the JSON file:', error);
        setData(null);
      }
    };
    fetchData();
  }, []);

  return data;
};

export default useVideoData;
