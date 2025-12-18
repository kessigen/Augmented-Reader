"use client";

import Header from "@/components/custom/Header";
import { motion } from "framer-motion";
import BookCard from "@/components/custom/BookCard";
import { useRef, useEffect, useState } from "react";
import { Hero } from "@/components/custom/Hero";
import { RecentReads } from "@/components/custom/RecentReads";
import UploadButton from "@/components/custom/UploadButton";

export default function Home() {
  const [AllBooks, setAllBooks] = useState<any>(null); // list of books fetched from backend
  const [loading, setLoading] = useState(true);
  const [fontSize, setFontSize] = useState<number>(16);


  // Fetch library on first load.
  useEffect(() => {
    const fetchAllBooks = async () => {
      try {
        setLoading(true);

        const response = await fetch(`http://127.0.0.1:8000/api/books/`);
        const data1 = await response.json();
        setAllBooks(data1);
        console.log(data1);
      } catch (error) {
        console.error("Error fetching book:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllBooks();
  }, []);

  // most recent books
  const lastBook = AllBooks?.[AllBooks.length - 1] ?? null;
  const LastTwo = AllBooks?.slice(-2) ?? [];

  // Uploads epub file whenever UploadButton is triggered
  const fileInputRef = useRef<HTMLInputElement>(null);
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };
  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await fetch("http://127.0.0.1:8000/api/books/upload/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const data = await response.json();
      console.log("Upload successful:", data);
      alert("Book uploaded successfully!");
    } catch (error) {
      console.error("Error uploading book:", error);
      alert("Error uploading file.");
    }
  };

  return (
    <>
      <Header />
      <main className=" mx-auto pt-10">
        <div>
          <div className="flex flex-col gap-4 mx-[30px]">
            <div className="flex gap-4 w-full">
              <div className="w-3/5 flex flex-col gap-4">
                <div className="py-4 pl-8">
                  <Hero book={lastBook} />
                </div>
              </div>

              <div className="w-2/5 bg-transparent px-6 pt-4 ">
                <p className="text-2xl font-extrabold pb-2">Recent Reads</p>
                <RecentReads books={LastTwo} />
              </div>
            </div>

            <div className="text-white py-4 px-6 rounded-[20px] bg-transparent w-full">
              <h1 className="  font-bold text-3xl pb-5 pt-2 whitespace-nowrap mr-4">
                LIBRARY
              </h1>
              <ul className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5 place-items-center">
                {
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".epub,.pdf"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                }
                {
                // Animate cards into 
                [
                  AllBooks
                    ? AllBooks.map((book, i) => (
                        <motion.li
                          key={i}
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          transition={{
                            type: "spring",
                            damping: 50,
                            mass: 0.75,
                          }}
                          initial={{ opacity: 0, x: 200 * (i + 1) }}
                          animate={{ opacity: 1, x: 0 }}
                        >
                          <a
                            href={`/book/${book.id}/1`}
                            style={{ textDecoration: "none" }}
                          >
                            <BookCard
                              title={book.title}
                              coverImage={book.cover_image}
                              description="summary TBD"
                            />
                          </a>
                        </motion.li>
                      ))
                    : [],
                ]}
              </ul>
            </div>
          </div>
        </div>

        <UploadButton onClick={handleUploadClick} />
      </main>
    </>
  );
}
