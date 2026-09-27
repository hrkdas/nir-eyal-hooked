// Sample notification worker demonstrating Owned external triggers and internal itch priming
export async function scheduleSmartDigest(userId: string) {
  // Owned Trigger: Context-aware push notification timed to user's daily morning routine
  await sendPushNotification(userId, {
    title: "3 colleagues updated your shared canvas",
    body: "Tap to review their feedback and keep the streak alive.",
    channel: "push_notification",
    priority: "high"
  });

  // Primed Trigger for next loop iteration
  await scheduleEmailDigest(userId, {
    subject: "Your weekly productivity summary is ready",
    sendAt: "09:00:00"
  });
}
