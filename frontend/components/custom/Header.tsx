"use client";
import { motion } from "framer-motion";
import Link from "next/link";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Command, CommandInput } from "@/components/ui/command";
import Image from "next/image";
import "@fortawesome/fontawesome-free/css/all.min.css";

export default function Header() {
  return (
    <header className=" w-full  flex justify-between items-center pr-0 py-2 pl-3 text-white bg-black">
      <motion.div
        className="flex items-center flex-nowrap "
        transition={{ type: "spring", damping: 18, mass: 0.75 }}
        initial={{ opacity: 0, x: -1000 }}
        animate={{ opacity: 1, x: 0 }}
      >
        <Image
          className=""
          src="/logo2.png"
          width={90}
          height={90}
          alt="logo"
        ></Image>
        <Image
          className="pl-2"
          src="/Aug.png"
          width={300}
          height={50}
          alt="logo"
        ></Image>
      </motion.div>
      <motion.div
        className="flex items-center flex-nowrap mr-25 "
        transition={{ type: "spring", damping: 18, mass: 0.75 }}
        initial={{ opacity: 0, x: -1000 }}
        animate={{ opacity: 1, x: 0 }}
      >
        <div className=" ml-2 flex flex-1 items-center ">
          <a
            className="font-bold  text-xl flex h-full items-center pr-4 text-gray-t0"
            href=""
          >
            <i className="fa fa-book pr-1"></i>Books
          </a>
          <a
            className="font-bold text-xl flex h-full items-center pr-4 text-gray-t0"
            href=""
          >
            <i className="fa fa-bookmark  pr-1"></i>Bookmarks
          </a>
          <a
            className="font-bold  text-xl flex h-full items-center pr-4 text-gray-t0"
            href=""
          >
            <i className="fa fa-comments  pr-1"></i>Forum
          </a>
          <a
            className="font-bold  text-xl flex h-full items-center pr-4 text-gray-t0"
            href=""
          >
            <i className="fa fa-gear  pr-1"></i>Settings
          </a>
        </div>
      </motion.div>

      <motion.div
        className="pr-3 flex items-center"
        transition={{ type: "spring", damping: 18, mass: 0.75 }}
        initial={{ opacity: 0, x: 1000 }}
        animate={{ opacity: 1, x: 0 }}
      >
        <Command className="w-5/6">
          <CommandInput placeholder="Search book..." />
        </Command>
        <Link href="/profile" className="px-3">
          <Avatar className="size-13">
            <AvatarImage src="https://i.pinimg.com/564x/2a/09/40/2a094063dfc15f573145f1d10af3212e.jpg" />
            <AvatarFallback>CN</AvatarFallback>
          </Avatar>
        </Link>
      </motion.div>
    </header>
  );
}
