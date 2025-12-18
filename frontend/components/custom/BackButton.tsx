"use client";
import { useRouter } from "next/navigation";

export default function BackButton({ bookId, lastChapter }) {
  const router = useRouter();

  const handleGoBack = async () => {
    try {
      await fetch(
        `http://127.0.0.1:8000/api/books/${bookId}/set_last/${lastChapter}/`,
        {
          method: "POST",
        }
      );
    } catch (err) {
      console.error("Failed to save chapter:", err);
    } finally {
      router.push("/");
    }
  };

  return (
    <i
      className="fas fa-chevron-left"
      style={{ fontSize: "20px", cursor: "pointer" }}
      onClick={handleGoBack}
    />
  );
}
