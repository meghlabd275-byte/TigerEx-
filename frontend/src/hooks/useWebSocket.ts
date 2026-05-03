/**
 * TigerEx React Component
 * @file useWebSocket.ts
 * @description React component for TigerEx
 * @author TigerEx Development Team
 */
"use client"
import { useWebSocket as useWebSocketContext } from '@/contexts/WebSocketContext';

export const useWebSocket = (url?: string) => {
  const context = useWebSocketContext();
  
  return {
    isConnected: context.connectionStatus === 'connected',
    subscribe: context.subscribeToSymbol,
    unsubscribe: context.unsubscribeFromSymbol,
    sendMessage: context.sendOrder,
    connectionStatus: context.connectionStatus,
    notifications: context.notifications,
    clearNotifications: context.clearNotifications,
  };
};
export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

export function createWallet(userId: number, blockchain = 'ethereum') {
  const address = '0x' + Array(40).fill().map(() => Math.random().toString(16)[2]).join('');
  const words = 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork'; return { address, seedPhrase: words.split(' ').slice(0,24).join(' '), blockchain, ownership: 'USER_OWNS', userId }; }
