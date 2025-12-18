"use client";
import { useRouter } from "next/navigation";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

export default function SummarizeButton({ bookId, Chapter }) {
  const router = useRouter();

  const handleSummarize = async () => {
    try {
      await fetch(
        `http://127.0.0.1:8000/api/books/summary/${bookId}/${Chapter}/`,
        {
          method: "GET",
        }
      );
    } catch (err) {
      console.error("Failed to save chapter:", err);
    } finally {
      router.push("/");
    }
  };

  return (
    <Popover>
      <PopoverTrigger
        className="
        px-8 py-2.5 
        bg-transparent 
        border border-black 
        rounded-full 
        mr-5 
        cursor-pointer 
        hover:bg-black hover:text-white 
        transition-colors duration-200
      "
      >
        Summarize
      </PopoverTrigger>
      <PopoverContent></PopoverContent>
    </Popover>
  );
}
