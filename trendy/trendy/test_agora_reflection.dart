import 'package:agora_rtm/agora_rtm.dart';

void main() {
  print('Available classes in agora_rtm package:');

  // Try to see what's exported by the package
  try {
    // Check if we can access any classes
    final client = RtmClient.createInstance('test-app-id');
    print('RtmClient.createInstance works');
  } catch (e) {
    print('Error with RtmClient: $e');
  }

  try {
    final message = RtmMessage.fromText('test message');
    print('RtmMessage.fromText works');
  } catch (e) {
    print('Error with RtmMessage: $e');
  }

  // Try to see what's available by checking the library
  try {
    final lib = agora_rtm;
    print('Library accessible: $lib');
  } catch (e) {
    print('Cannot access library directly: $e');
  }
}
