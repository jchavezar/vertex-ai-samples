"use client";

import Link from "next/link";
import Image from "next/image";
import { flagUrl } from "@/data/teams";

type Size = "sm" | "md" | "lg";

const SIZE_MAP: Record<Size, { flag: number; px: string; text: string }> = {
  sm: { flag: 40,  px: "w-5 h-5",  text: "text-xs" },
  md: { flag: 64,  px: "w-7 h-7",  text: "text-sm" },
  lg: { flag: 80,  px: "w-9 h-9",  text: "text-base" },
};

type Props = {
  code: string;
  name: string;
  iso2: string;
  size?: Size;
  showName?: boolean;
  className?: string;
};

export function TeamChip({ code, name, iso2, size = "md", showName = true, className = "" }: Props) {
  const { flag, px, text } = SIZE_MAP[size];
  return (
    <Link
      href={`/equipos/${code}`}
      className={`inline-flex items-center gap-1.5 hover:opacity-80 transition-opacity ${className}`}
      title={name}
    >
      <span className={`relative ${px} rounded overflow-hidden flex-shrink-0`}>
        <Image src={flagUrl(iso2, flag)} alt={name} fill sizes={`${flag}px`} className="object-cover" unoptimized />
      </span>
      {showName && <span className={`font-display font-semibold ${text}`}>{name}</span>}
    </Link>
  );
}
