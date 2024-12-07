import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Chat de consulta sobre Legalidad y Protección de la Información',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const LegalInfoChatScreen(),
    );
  }
}

class LegalInfoChatScreen extends StatefulWidget {
  const LegalInfoChatScreen({super.key});

  @override
  _LegalInfoChatScreenState createState() => _LegalInfoChatScreenState();
}

class _LegalInfoChatScreenState extends State<LegalInfoChatScreen> {
  final TextEditingController _questionController = TextEditingController();
  String _response = '';
  bool _isLoading = false;

  Future<void> sendQuestion(String question) async {
    setState(() {
      _isLoading = true;
    });

    try {
      final url = Uri.parse(
          'http://127.0.0.1:8000/ask'); // Cambia si usas otro host o puerto
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'question': question}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        setState(() {
          _response = data['answer'] ?? 'No response from the server.';
        });
      } else {
        setState(() {
          _response =
              'Error: ${response.statusCode} - ${response.reasonPhrase}';
        });
      }
    } catch (e) {
      setState(() {
        _response = 'Error: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Chat de consulta sobre Legalidad y Protección de la Información.',
        ),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Image.asset(
              'assets/logo.png', // Ruta del logo (asegúrate de tener el archivo en assets)
              height: 200,
            ),
            const SizedBox(height: 8), // Espacio entre el logo y el texto
            const Text(
              'Este es un chat que responde preguntas sobre legalidad y protección de la información',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
            TextField(
              controller: _questionController,
              decoration: const InputDecoration(
                labelText: 'Realiza una pregunta',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                if (_questionController.text.isNotEmpty) {
                  sendQuestion(_questionController.text);
                }
              },
              child: const Text('Enviar'),
            ),
            const SizedBox(height: 16),
            if (_isLoading)
              const CircularProgressIndicator()
            else
              Expanded(
                child: SingleChildScrollView(
                  child: Text(
                    _response,
                    style: const TextStyle(fontSize: 16),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
