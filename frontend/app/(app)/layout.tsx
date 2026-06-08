import { AppSidebar } from "@/components/app-sidebar";
import { AppTopbar } from "@/components/app-topbar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-shell gradient-bg">
      <AppSidebar />
      <div className="app-main">
        <AppTopbar />
        <main className="app-content">{children}</main>
      </div>
    </div>
  );
}
