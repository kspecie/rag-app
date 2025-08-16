// import { toast as sonnerToast, ToastOptions } from 'sonner';

// export function useToast(): {toast: (options: ToastOptions) => void } {
//   return {
//     toast: sonnerToast,
//   };
// }

// import { toast as sonnerToast, ToastOptions} from 'sonner';

// interface CustomToastOptions extends ToastOptions {
//     title?: string;
//   }

// export function useToast(): { toast: (options: ToastOptions) => void } {
//   return {
//     toast: (message: string, options?: CustomToastOptions) => {
//         toast(message, options);
//   };
// }


// import { toast as sonnerToast } from 'sonner';

// interface CustomToastOptions {
//   title?: string;
//   description?: string;
//   duration?: number;
//   action?: () => void;
//   // Add other props you need based on Sonner's toast function
// }

// export function useToast() {
//   return {
//     toast: (message: string, options?: CustomToastOptions) => {
//       sonnerToast(message, options);
//     },
//   };
// }


// import { toast as sonnerToast, type Toast as SonnerToast } from 'sonner';

// export function useToast() {
//   return {
//     toast: (message: string, options?: Parameters<typeof sonnerToast>[1]) => {
//       sonnerToast(message, options);
//     },
//   };
// }


import { toast as sonnerToast } from 'sonner';

export function useToast() {
  return {
    toast: (message: string, options?: Parameters<typeof sonnerToast>[1]) => {
      sonnerToast(message, options);
    },
  };
}
