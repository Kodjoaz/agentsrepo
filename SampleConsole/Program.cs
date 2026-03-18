using SampleLibrary;

var name = args.Length > 0 ? args[0] : "Developer";
var message = Greeter.SayHello(name);

Console.WriteLine(message);