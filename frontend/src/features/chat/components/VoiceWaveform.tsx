"use client";

import { motion } from "framer-motion";

export function VoiceWaveform() {
  return (
    <div className="flex h-8 items-end gap-1 px-1" aria-hidden>
      {Array.from({ length: 8 }).map((_, index) => (
        <motion.span
          key={index}
          className="w-1 rounded-full bg-cyan-400"
          animate={{ height: ["30%", "100%", "40%"] }}
          transition={{
            repeat: Infinity,
            duration: 0.8,
            delay: index * 0.08,
            ease: "easeInOut",
          }}
          style={{ height: "30%" }}
        />
      ))}
    </div>
  );
}
