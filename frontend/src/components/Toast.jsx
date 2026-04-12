import { AnimatePresence, motion } from 'framer-motion';

export default function Toast({ message }) {
  return (
    <div className="toast-container">
      <AnimatePresence>
        {message && (
          <motion.div
            className="toast-msg"
            initial={{ opacity: 0, y: 30, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 30, scale: 0.9 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
          >
            {message}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
