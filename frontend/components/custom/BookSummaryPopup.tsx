"use client";

import React, { useState, useEffect } from "react";

interface BookSummaryPopupProps {
  bookId: number;
  chapterId: number;
}

const BookSummaryPopup: React.FC<BookSummaryPopupProps> = ({
  bookId,
  chapterId,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [data, setData] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      setError(null);
      setData("");

      fetch(`http://127.0.0.1:8000/api/books/summary/${bookId}/${chapterId}/`)
        .then((res) => {
          console.log(res);
          if (!res.ok) throw new Error("Failed to fetch summary");
          return res.json();
        })
        .then((data) => {
          setData(data.summary || "No summary found.");
        })
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [isOpen, bookId, chapterId]);

  return (
    <div className="">
      <button
        onClick={() => setIsOpen(true)}
        className="mr-200 px-6 py-2 bg-gray-100 text-black rounded-lg hover:bg-gray-500 "
      >
        Summarize Previous Chapters
      </button>

      {isOpen && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-50">
          <div
            className="
    bg-white rounded-lg shadow-lg p-6 
    w-[700px] max-w-[90vw] 
    max-h-[80vh] 
    overflow-y-auto resize-x 
    text-left
  "
          >
            <h2 className="text-lg font-semibold mb-4">Book Summary so far</h2>

            {loading && <p>Loading summary...</p>}
            {error && <p className="text-red-500">{error}</p>}
            {!loading && !error && (
              <p className="text-gray-700 whitespace-pre-line">{data}</p>
            )}

            <button
              onClick={() => setIsOpen(false)}
              className="mt-4 px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-900 transition"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default BookSummaryPopup;
