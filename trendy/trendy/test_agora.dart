import 'package:agora_rtm/agora_rtm.dart';

void main() {
  // Test to see what classes are available in the agora_rtm package
  print('Testing Agora RTM package...');

  // Try to create an instance to see what classes are available
  try {
    // Check if we can create a client
    final client = AgoraRtmClient.createInstance('test-app-id');
    print('AgoraRtmClient.createInstance works');
  } catch (e) {
    print('Error creating AgoraRtmClient: $e');
  }

  // Try to create a message
  try {
    final message = AgoraRtmMessage.fromText('test message');
    print('AgoraRtmMessage.fromText works');
  } catch (e) {
    print('Error creating AgoraRtmMessage: $e');
  }
}
