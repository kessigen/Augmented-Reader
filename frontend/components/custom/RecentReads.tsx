import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

import { TagBadges } from "./TagGenerator";

export function RecentReads({ books }: any) {
  return (
    <div className="h-full ">
      <Card className="mb-5 bg-accent text-black h-[120px]">
        <div className="flex h-fit">
          <div className="flex items-center justify-center">
            <img
              src={books?.[0]?.cover_image || "/bg-Alice.jpg"}
              alt="thumb"
              className="w-[80px] h-[80px] ml-2 object-cover rounded-md"
            />
          </div>

          <div className="flex flex-col justify-center flex-1">
            <CardHeader className="">
              <CardTitle className="text-l">
                {books?.[0]?.title || "Alice In WonderLand"}
              </CardTitle>
              <CardDescription className="">
                <TagBadges
                  tags={books?.[0]?.tags || ["Fantasy", "Children"]}
                  variant="default"
                />
              </CardDescription>
              <CardDescription className="">Chapters: 3/14</CardDescription>
            </CardHeader>

            <CardContent className="py-0">
              <Progress value={33} className="w-full" />
            </CardContent>
          </div>
        </div>
      </Card>

      <Card className="mb-5 bg-accent text-black h-[120px]">
        <div className="flex h-fit">
          <div className="flex items-center justify-center">
            <img
              src={books?.[1]?.cover_image || "/bg-frank.jpg"}
              alt="thumb"
             className="w-[80px] h-[80px] ml-2 object-cover rounded-md"/>
          </div>

          <div className="flex flex-col justify-center flex-1">
            <CardHeader className="">
              <CardTitle className="text-l">
                {books?.[1]?.title || "Frankenstein"}
              </CardTitle>
              <CardDescription className="">
                <TagBadges
                  tags={books?.[1]?.tags || ["Suspense", "Horror", "Tragedy"]}
                  variant="default"
                />
              </CardDescription>
              <CardDescription className="">Chapters: 7/24</CardDescription>
            </CardHeader>

            <CardContent className="py-0">
              <Progress value={33} className="w-full" />
            </CardContent>
          </div>
        </div>
      </Card>
    </div>
  );
}
