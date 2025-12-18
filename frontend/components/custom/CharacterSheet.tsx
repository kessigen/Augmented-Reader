"use client";

import { Card, CardContent } from "@/components/ui/card";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";

type Props = {
  open: boolean;
  onClose: () => void;
  characters: any[];
};

export default function CharacterSheet({ open, onClose, characters }: Props) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div className="relative bg-white rounded-xl p-6 w-[1200px] h-auto max-w-3xl shadow-2xl overflow-hidden">
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-600 hover:text-black text-2xl font-bold"
        >
          ✕
        </button>

        <h2 className="text-center text-xl font-semibold mb-4">
          Character Sheet
        </h2>

        {characters.length > 0 ? (
          <Carousel
            opts={{
              align: "start",
              loop: true,
            }}
            className="w-full max-w-5xl mx-auto"
          >
            <CarouselContent className="flex items-center">
              {characters.map((char, index) => (
                <CarouselItem key={index} className="basis-auto flex justify-center">
                  <div className="p-3">
                    <Card className="w-[480px] h-auto shadow-md flex items-center">
                      <CardContent className="flex flex-row items-center p-4 space-x-4">
                        {char.image ? (
                          <img
                            src={`http://127.0.0.1:8000${char.image}`}
                            alt={char.name}
                            className="w-40 h-52 object-cover rounded-lg shadow-sm"
                          />
                        ) : (
                          <div className="w-40 h-52 flex items-center justify-center bg-gray-200 rounded-lg text-gray-500">
                            No Image
                          </div>
                        )}

                        <div className="flex flex-col text-left space-y-1 w-[250px]">
                          <h3 className="text-lg font-bold text-gray-800">
                            {char.name}
                          </h3>
                          <p className="text-sm italic text-gray-600">{char.role}</p>
                          {char.gender && (
                            <p className="text-sm text-gray-500">
                              Gender: {char.gender}
                            </p>
                          )}
                          {char.personality && (
                            <p className="text-xs text-gray-700 line-clamp-3">
                              {char.personality}
                            </p>
                          )}
                          {char.bio && (
                            <p className="text-xs text-gray-500 line-clamp-4">
                              {char.bio}
                            </p>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </CarouselItem>
              ))}
            </CarouselContent>

            <CarouselPrevious className="absolute left-2 top-1/2 -translate-y-1/2 z-50" />
            <CarouselNext className="absolute right-2 top-1/2 -translate-y-1/2 z-50" />
          </Carousel>
        ) : (
          <p className="text-center text-gray-500">No characters found.</p>
        )}
      </div>
    </div>
  );
}
