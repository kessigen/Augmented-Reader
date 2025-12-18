import * as React from "react";

import { Card, CardContent } from "@/components/ui/card";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
} from "@/components/ui/carousel";
import { TagBadges } from "./TagGenerator";

export function Hero({ book }: any) {
  return (
    <Carousel className="w-full h-full ">
      <CarouselContent className=" px-0 ">
        {Array.from({ length: 3 }).map((_, index) => (
          <CarouselItem key={index}>
            <div className="p-1   h-full ">
              <Card
                className="
    h-80 m-0 w-full bg-no-repeat bg-size-[100%_100%] bg-[linear-gradient(to_bottom,rgba(0,0,0,0),#0a1a3f),url(/bg-Alice.jpg)] "
              >
                <CardContent className="flex flex-col justify-end items-start gap-2  pt-30 h-full text-white">
                  <p className="text-3xl text-bold">
                    {book?.title ?? "Alice In WonderLand"}
                  </p>
                  <TagBadges
                    tags={book?.tags ?? ["Fantasy", "Literature"]}
                    className=" text-white"
                  />
                  <p className="text-l  mt-5 line-clamp-2 w-7/10">
                    {book?.synopsis ?? "synopsis loading"}
                  </p>
                </CardContent>
              </Card>
            </div>
          </CarouselItem>
        ))}
      </CarouselContent>
    </Carousel>
  );
}
