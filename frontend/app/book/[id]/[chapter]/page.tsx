"use client";
import "@fortawesome/fontawesome-free/css/all.min.css";
import { motion } from "framer-motion";
import { useParams, useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import styles from "./book.module.css";
import InteractiveParagraph from "@/components/custom/InteractiveParagraph";
import BackButton from "@/components/custom/BackButton";
import PopChat from "@/components/custom/PopChat";
import BookSummaryPopup from "@/components/custom/BookSummaryPopup";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";

import parse, { domToReact } from "html-react-parser";
import { Music } from "lucide-react";
import MusicButton from "@/components/custom/MusicButton";
import RelationshipGraph from "@/components/custom/RelationshipGraph";
import CharacterSheet from "@/components/custom/CharacterSheet";

export default function BookPage() {
  //
  const { id, chapter } = useParams();
  const [selectedBook, setSelectedBook] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [fontSize, setFontSize] = useState<number>(16);
  // toggle for charcter sheet visibility
  const [showCarousel, setShowCarousel] = useState(false);
  // toggle for relationship graph visibility
  const [showGraph, setShowGraph] = useState(false);
  const [characters, setCharacters] = useState<any[]>([]);

  //Fetch specific chapter of book from backend
  useEffect(() => {
    const fetchBook = async () => {
      try {
        setLoading(true);

        const response = await fetch(
          `http://127.0.0.1:8000/api/books/${id}/chapters/${chapter}/`
        );
        const data = await response.json();
        setSelectedBook(data);
        console.log(data);
      } catch (error) {
        console.error("Error fetching book:", error);
        toast.error("Failed to load book chapter");
      } finally {
        setLoading(false);
      }
    };

    if (id && chapter) {
      fetchBook();
    }
  }, [id, chapter]);

  //Fetch  chracter information from backend
  useEffect(() => {
    const fetchCharacters = async () => {
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/api/books/${id}/characters/`
        );
        if (!res.ok) throw new Error("Failed to fetch characters");
        const data = await res.json();
        setCharacters(data);
      } catch (err) {
        console.error("Error fetching characters:", err);
        toast.error("Failed to load characters");
      }
    };
    if (id) fetchCharacters();
  }, [id]);

  // font size variables
  const increaseFont = () => setFontSize((prev) => Math.min(prev + 2, 32));
  const decreaseFont = () => setFontSize((prev) => Math.max(prev - 2, 10));

  if (loading) return <div className="center">Loading...</div>;
  if (!selectedBook) return <p>Book chapter not found</p>;

  //Word count calculation
  const words = selectedBook.content.trim()
    ? selectedBook.content.trim().split(/\s+/).length
    : 0;
  const WPM = 260;
  const minutes = words > 0 ? Math.max(1, Math.round(words / WPM)) : 0;

  return (
    <motion.div
      transition={{ type: "spring", damping: 40, mass: 0.75 }}
      initial={{ opacity: 0, x: 1000 }}
      animate={{ opacity: 1, x: 0 }}
    >
      <motion.section
        transition={{ type: "spring", damping: 44, mass: 0.75 }}
        initial={{ opacity: 0, y: -1000 }}
        animate={{ opacity: 1, y: 0 }}
        className={styles.appBar}
      >
        <div className={styles.leftIcons}>
          <BackButton bookId={id} lastChapter={chapter} />
        </div>

        {/* text summarization feature */}

        <BookSummaryPopup bookId={Number(id)} chapterId={Number(chapter)} />

        {/* buttons in header */}
        <div>
          {/*text size buttons */}
          <button
            className="bg-transparent border-2 mr-1 border-white px-3 py-1 rounded-md hover:bg-gray-700 transition"
            onClick={decreaseFont}
            title="Decrease text size"
          >
            A-
          </button>
          <button
            className="bg-transparent border-2 border-white px-3 py-1 mr-3 ml-2 rounded-md hover:bg-gray-700 transition"
            onClick={increaseFont}
            title="Increase text size"
          >
            A+
          </button>

          {/*toggle character sheet visibility*/}
          <i
            style={iconStyle}
            className="fa-solid fa-list cursor-pointer hover:text-accent transition"
            onClick={() => setShowCarousel(true)}
          ></i>

          {/*toggle relationship graph visibility*/}
          <i
            style={iconStyle}
            className="fa-solid fa-diagram-project"
            onClick={() => setShowGraph(true)}
          />

          {/*toggle play background music*/}
          <MusicButton musicType={selectedBook.music} />

          {/*next/previous chapters*/}
          <Link href={`/book/${id}/${Number(chapter) + 1}`}>
            <img
              className="next_ch hide-2s rotate-180 "
              src="/left1.png"
              alt=" icon"
              width={60}
              height={60}
              style={{ borderRadius: "50%", cursor: "pointer" }}
            />
          </Link>
          <Link href={`/book/${id}/${Number(chapter) - 1}`}>
            <img
              className="prev_ch hide-2s "
              src="/left1.png"
              alt=" icon"
              width={60}
              height={60}
              style={{ borderRadius: "50%", cursor: "pointer" }}
            />
          </Link>
        </div>
      </motion.section>

      {/*chapter text content*/}
      <main
        className="bookContainer chapter-content"
        style={{ fontSize: `${fontSize}px` }}
      >
        {/*chapter text header*/}
        <h1 className="center font-stretch-500%">
          <b>{selectedBook.title}</b>
        </h1>
        <p className="center small text-gray-300 mt-0 mb-1">
          By {selectedBook.author}
          {words > 0 && (
            <>
              {" "}
              <br /> {words.toString()} words · {minutes} min read
            </>
          )}
        </p>

        <hr className="border-t border-white mt-0 mb-4" />

        <div className="space-y-20">
          <div className="space-y-20">
            {/*splits full chapter text into event sections*/}
            {parse(selectedBook.content, {
              replace: (domNode: any) => {
                {
                  /* identifies backend injected markers for event separators e.g 'ev01' for processing*/
                }
                if (
                  domNode.type === "tag" &&
                  domNode.name === "div" &&
                  domNode.attribs?.id?.startsWith("ev")
                ) {
                  const id = domNode.attribs.id;
                  const eventIndex = parseInt(id.slice(2), 10);
                  return (
                    <div className="my-4">
                      {/*displays small widget at the end of each event for image generation*/}
                      <InteractiveParagraph
                        bookId={selectedBook.id}
                        chapterId={Number(chapter)}
                        event_number={eventIndex}
                      >
                        <p className="invisible"> Event {eventIndex} marker</p>
                      </InteractiveParagraph>
                    </div>
                  );
                }

                return undefined;
              },
            })}
          </div>
        </div>
      </main>

      {/*character sheet component*/}
      <CharacterSheet
        open={showCarousel}
        onClose={() => setShowCarousel(false)}
        characters={characters}
      />

      {/*toggle relationship graph display*/}
      {showGraph && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
          <div className="relative bg-white rounded-xl p-6 w-[1200px] h-auto max-w-5xl shadow-2xl overflow-hidden">
            <button
              onClick={() => setShowGraph(false)}
              className="absolute top-3 right-3 z-50 text-gray-600 hover:text-black text-2xl font-bold"
            >
              ✕
            </button>

            <h2 className="relative z-50 text-center text-xl font-semibold mb-1 text-black">
              Relationship Graph
            </h2>
            <p className="relative z-50 text-center text-sm text-gray-500 mb-4">
              Drag nodes to move
            </p>

            <div className="relative z-0 flex items-center justify-center">
              {/*relationship graph component*/}

              <RelationshipGraph bookId={selectedBook.id} />
            </div>
          </div>
        </div>
      )}

       {/*book assistant component*/}
      <PopChat bookId={Number(id)} />

      <ToastContainer />
    </motion.div>
  );
}

const iconStyle = {
  marginRight: "20px",
  fontSize: "20px",
};
