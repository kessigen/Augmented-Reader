export default function BookCard({
  title,
  description,
  coverImage,
  onClick,
}: any) {
  return (
    <div
      className="bg-transparent text-white w-[280px] h-[450px] rounded-[5px]   cursor-pointer transition-transform duration-300 ease-in-out mb-6 mr-4 hover:scale-[1.02]"
      onClick={onClick}
    >
      <img
        src={coverImage}
        alt={title}
        className="w-full h-5/6 aspect-square rounded-[8px]"
      />
      <div className=" ">
        <h3 className="text-[1.2rem] font-bold m-2 line-clamp-2">{title}</h3>
      </div>
    </div>
  );
}
