"use client";

export default function MusicButton({ musicType }: { musicType?: string }) {
  const tracks = ["neutral", "hopeful", "tense", "sad", "dark"];
  if (!tracks.includes(musicType || "")) {
    musicType = "neutral";
  }
  const toggleMusic = () => {
    const audio = document.getElementById(
      "bg-audio"
    ) as HTMLAudioElement | null;
    if (!audio) return;

    if (audio.paused) {
      audio.play();
    } else {
      audio.pause();
    }
  };

  return (
    <>
      <audio id="bg-audio" src={`/music/${musicType}.mp3`} loop />
      <i
        className="fa-solid fa-music text-[20px] "
        onClick={() => toggleMusic()}
      ></i>
    </>
  );
}
