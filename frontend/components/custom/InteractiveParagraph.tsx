"use client";
import { useState } from "react";
import { Copy, Play, RotateCcw } from "lucide-react";
import { toast } from "react-toastify";

interface SceneData {
  imageUrl: string;
  caption: string;
}

interface ParagraphProps {
  children: React.ReactNode;
  event_number: number;
  bookId: number;
  chapterId: number;
}
export default function InteractiveParagraph({  children,event_number,  bookId, chapterId,}: ParagraphProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [scene, setScene] = useState<SceneData | null>(null);
  const [isLoadingScene, setIsLoadingScene] = useState(false);

  const handleCopy = () => {
    const text = children?.toString() || "";
    navigator.clipboard.writeText(text);
    toast.success("Text copied to clipboard!");
  };

  const handleReload = () => {
    toast.success("Feature coming soon");
  };

  const handleImageScene = async () => {
    try {
      setIsLoadingScene(true);

      const response = await fetch(
        `http://127.0.0.1:8000/api/books/${bookId}/chapters/${chapterId}/scene/${event_number}/`,
        {
          method: "GET",
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      const data = await response.json();
      setScene({
        imageUrl: data.image_url,
        caption: data.caption,
      });

      toast.success("Scene image loaded!");
    } catch (error) {
      console.error("Error loading scene image:", error);
      toast.error("Could not load scene image.");
    } finally {
      setIsLoadingScene(false);
    }
  };

  return (
    <div
      className="relative mb-6"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {children}

      {isHovered && (
        <div className="absolute top-3 right-2 flex gap-2 bg-accent backdrop-blur-sm rounded-lg shadow-lg p-1.5 border z-10">
          <button
            onClick={handleCopy}
            className="p-1.5 hover:bg-gray-100 rounded transition-colors"
            title="Copy"
          >
            <Copy size={14} className="text-gray-600" />
          </button>
          <button
            onClick={handleImageScene}
            className="p-1.5 hover:bg-gray-100 rounded transition-colors"
            title="Play"
          >
            <Play size={14} className="text-gray-600" />
          </button>
          <button
            onClick={handleReload}
            className="p-1.5 hover:bg-gray-100 rounded transition-colors"
            title="Reload"
          >
            <RotateCcw size={14} className="text-gray-600" />
          </button>
        </div>
      )}
      {!isHovered && !scene && (
        <div className="absolute bottom-0 left-160 right-160 h-px bg-white" />
      )}
      {isHovered && !scene && (
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gray-500" />
      )}
      {scene && (
        <div className="mt-3 flex flex-col gap-4 items-center">
          {scene.imageUrl && (
            <img
              src={scene.imageUrl}
              alt={scene.caption || "Generated image"}
              className="w-200 h-auto rounded-md border"
            />
          )}
          {scene.caption && (
            <p className="text-sm text-gray-300">{scene.caption}</p>
          )}
        </div>
      )}
    </div>
  );
}
