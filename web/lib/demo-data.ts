/**
 * Sample data for the family view demonstration at /demo.
 *
 * Invented, but not made up: every alert below is modelled on a scam pattern
 * that actually runs against older people on Facebook and Instagram — cloned
 * profiles, a "relative" in trouble, support impersonation, romance fraud,
 * and deepfaked endorsements. Nothing here is a real person.
 */

import type { Risk } from "./types";

export interface DemoAlert {
  id: string;
  risk: Risk;
  kind: "message" | "video" | "profile";
  when: string;
  where: "Facebook" | "Instagram" | "Messenger" | "YouTube";
  /** What arrived. */
  headline: string;
  /** The quoted content, as she saw it. */
  quote?: string;
  /** What RUAI told her, in the words it used. */
  told: string;
  /** What happened next. */
  outcome: string;
  outcomeTone: "good" | "neutral" | "attention";
}

export const PARENT = {
  name: "Ruth",
  relationship: "Your mother",
  age: 78,
  lastActive: "20 minutes ago",
  protectedSince: "March",
};

export const DEMO_STATS = [
  { value: "63", label: "Things checked this week" },
  { value: "4", label: "Scams stopped", tone: "danger" as const },
  { value: "2", label: "Fake profiles spotted", tone: "danger" as const },
  { value: "£0", label: "Money lost", tone: "safe" as const },
];

export const DEMO_ALERTS: DemoAlert[] = [
  {
    id: "1",
    risk: "danger",
    kind: "profile",
    when: "Yesterday, 8:42pm",
    where: "Messenger",
    headline: "Someone copied her cousin Margaret's profile",
    quote:
      "Ruth love, it's Margaret. I lost my old account. I'm stuck abroad and my card has been blocked — could you send £400 in gift cards? I'll pay you back Friday, please don't tell the family.",
    told:
      "This looks like a scam. Someone has copied a profile you know. Real Margaret would not ask for gift cards.",
    outcome: "She closed it and rang the real Margaret. Margaret was at home.",
    outcomeTone: "good",
  },
  {
    id: "2",
    risk: "danger",
    kind: "video",
    when: "Tuesday, 2:15pm",
    where: "Facebook",
    headline: "An investment video using a deepfaked news presenter",
    told:
      "This video was probably made by AI. The presenter's mouth does not match the words, and the station logo changes between frames.",
    outcome: "She watched the warning and scrolled past. No link was opened.",
    outcomeTone: "good",
  },
  {
    id: "3",
    risk: "danger",
    kind: "message",
    when: "Tuesday, 9:03am",
    where: "Facebook",
    headline: "A message claiming to be Facebook Support",
    quote:
      "FINAL NOTICE: your account will be permanently deleted in 24 hours due to a copyright complaint. Confirm your identity now at fb-appeal-centre.co to keep your photos.",
    told:
      "This looks like a scam. Facebook does not send messages like this, and the address is not a Facebook one.",
    outcome: "She asked you about it first. You confirmed it was fake.",
    outcomeTone: "good",
  },
  {
    id: "4",
    risk: "caution",
    kind: "profile",
    when: "Monday, 7:20pm",
    where: "Instagram",
    headline: "A new account has been very affectionate very quickly",
    quote:
      "Good evening my dear Ruth. I think about you all day. I am a widower too, working offshore. I feel we were meant to find each other.",
    told:
      "Be careful with this message. Strong affection this early is how romance scams begin. There is no rush.",
    outcome: "Still talking to them. Worth a gentle conversation.",
    outcomeTone: "attention",
  },
  {
    id: "5",
    risk: "caution",
    kind: "message",
    when: "Sunday, 11:48am",
    where: "Facebook",
    headline: "A prize she had not entered for",
    quote:
      "Congratulations Ruth! You have been selected in our anniversary giveaway. Claim your £5,000 by paying the £29 delivery fee today.",
    told:
      "Be careful with this message. Real prizes do not arrive by surprise, and they never ask for a fee.",
    outcome: "She deleted it without replying.",
    outcomeTone: "good",
  },
  {
    id: "6",
    risk: "safe",
    kind: "video",
    when: "Sunday, 10:12am",
    where: "YouTube",
    headline: "A gardening video she wanted to check",
    told: "This looks like a real video. We did not find signs a computer made it.",
    outcome: "She carried on watching.",
    outcomeTone: "neutral",
  },
];

export const DEMO_INSIGHTS = [
  {
    title: "Two of this week's messages came from accounts made in the last month",
    body: "Brand-new accounts contacting someone who is not looking for new contacts is one of the clearest early signals.",
  },
  {
    title: "Every money request this week asked for gift cards",
    body: "It is the route scammers prefer because it cannot be reversed. Ruth has now been shown that three times, in the same words.",
  },
  {
    title: "She checked something herself four times",
    body: "She is using the button rather than waiting to be warned. That is the outcome worth aiming for.",
  },
];

export const DEMO_SOURCES = [
  { label: "Facebook", share: 52, tone: "danger" as const },
  { label: "Instagram", share: 27, tone: "caution" as const },
  { label: "YouTube", share: 15, tone: "safe" as const },
  { label: "Elsewhere", share: 6, tone: "neutral" as const },
];

export const DEMO_SETTINGS = [
  {
    label: "Text me about serious warnings",
    note: "Only for the ones RUAI is confident about. Two messages this week.",
    on: true,
  },
  {
    label: "Send me a Sunday summary",
    note: "One email, so nobody has to check a dashboard to feel reassured.",
    on: true,
  },
  {
    label: "Tell Ruth when I have been notified",
    note: "On by default. Watching someone without their knowledge is not care.",
    on: true,
  },
  {
    label: "Let me see the full message text",
    note: "Off by default. She can share a message, but it is hers to share.",
    on: false,
  },
];
