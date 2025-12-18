import { Badge } from "@/components/ui/badge";

type BadgeProps = {
  tags: string[];
  variant?: any;
  className?: any;
};

export function TagBadges({
  tags,
  variant = "outline",
  className = null,
}: BadgeProps) {
  if (!tags?.length) return null;

  return (
    <div>
      {tags.map((t) => (
        <Badge key={t} variant={variant} className={`mr-1 ${className}`}>
          {t}
        </Badge>
      ))}
    </div>
  );
}
