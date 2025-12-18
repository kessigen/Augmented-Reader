"use client";

import React, { useState, useRef, useEffect } from "react";
import Image from "next/image";
import "./UploadButton.css";

export default function BookCard({ onClick }: any) {
  return (
    <div id="chatCon">
      <div className="pop cursor-pointer transition-transform duration-300 ease-in-out mb-6 mr-4 hover:scale-[1.25]">
        <p>
          <img
            onClick={onClick}
            src="/U1.png"
            alt="Chat icon"
            width={500}
            height={500}
            style={{ borderRadius: "50%", cursor: "pointer" }}
          />
        </p>
      </div>
    </div>
  );
}
